from dataclasses import dataclass
from functools import partial
from typing import Callable, Dict

import pandas as pd
import streamlit as st
from forex_python.converter import CurrencyRates

import project_get_data as data


@st.cache(show_spinner=True)
def get_exchange_rates(currencies):
    """Get the exchange rates for a given list of currencies"""
    rates = CurrencyRates()
    return {currency: rates.get_rate(currency, "CNY") for currency in currencies}


@dataclass
class WebScrapper:
    """Webscrapper tool to get product, price, and potentially image"""

    scrapping_function: Callable[[str], pd.DataFrame]
    currency: str
    source: str


@st.cache(show_spinner=True)
def get_lego_df(
    lego_name: str, lego_id: int, exchange_rates: Dict[str, float]
) -> pd.DataFrame:
    """Get a DataFrame with information about the lego box from the different websites"""
    print(f"Searching Lego {lego_name} (id={lego_id})")

    def get_data(scrapper: WebScrapper) -> pd.DataFrame:
        """Get dataframe from a webscrapper website"""
        try:
            df = scrapper.scrapping_function(f"lego {lego_id}")
            df["source"] = scrapper.source
            if scrapper.currency != "CNY":
                df["price"] = df["price"] * exchange_rates[scrapper.currency]
        except Exception as e:
            print(
                f"Error getting Lego {lego_id} ({lego_name}) from {scrapper.source}: {e}"
            )
            df = pd.DataFrame()
        return df

    web_scrappers = [
        WebScrapper(data.get_df_jd, "CNY", source="JD"),
        WebScrapper(data.get_df_amazon, "GBP", source="Amazon UK"),
        WebScrapper(
            partial(data.get_df_amazon, domain="de"), "EUR", source="Amazon DE"
        ),
        WebScrapper(data.get_df_newegg, "USD", source="Newegg"),
    ]

    # We need to join all the data and filtering wrong results
    # that don't match the ID of the Lego we are searching
    df = pd.concat([get_data(scrap) for scrap in web_scrappers], ignore_index=True)
    df = df[df.name.str.contains(str(lego_id))]
    df["legoID"] = lego_id
    df["legoName"] = lego_name

    return df


@st.cache
def get_lego_image_url(lego_id: int, df: pd.DataFrame) -> str:
    """Get URL of the picture of a given lego, if any"""
    try:
        images = df[df.legoID == lego_id]["image"]
        return images.iloc[0]
    except KeyError:
        return ""
