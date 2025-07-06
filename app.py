import streamlit as st
import pandas as pd
import yfinance as yf
from fredapi import Fred
import plotly.graph_objects as go

# Config
st.set_page_config(page_title="Isaura's Macro Dashboard", layout="wide")
st.title(" Isaura's Macro Dashboard")

# Load FRED
fred = Fred(api_key=st.secrets["fred"]["api_key"])

# Load CPI data for inflation calculations
@st.cache_data
def load_cpi_data():
    """Load and calculate CPI inflation rate"""
    try:
        cpi = fred.get_series("CPIAUCSL", start="1990-01-01").dropna()
        # Calculate year-over-year inflation rate
        cpi_inflation = cpi.pct_change(periods=12) * 100
        return cpi_inflation.dropna()
    except Exception as e:
        st.error(f"Error loading CPI data: {e}")
        return pd.Series()

# Tabs - Updated to include IWM
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Treasury Yields", "SPY (S&P 500)", "IWM (Russell 2000)", "Dollar Index (UUP)", "Federal Reserve", "VIX"])

# --- TAB 1: Treasury Yields ---
with tab1:
    st.header(" Treasury Yields")
    
    # Sub-tabs for different Treasury yields
    subtab1, subtab2, subtab3, subtab4, subtab5, subtab6, subtab7 = st.tabs(["3M", "1Y", "3Y", "5Y", "10Y", "20Y", "30Y"])
    
    # Treasury yield FRED series codes
    treasury_codes = {
        "3M": {"code": "DGS3MO", "name": "3-Month Treasury Yield"},
        "1Y": {"code": "DGS1", "name": "1-Year Treasury Yield"},
        "3Y": {"code": "DGS3", "name": "3-Year Treasury Yield"},
        "5Y": {"code": "DGS5", "name": "5-Year Treasury Yield"},
        "10Y": {"code": "DGS10", "name": "10-Year Treasury Yield"},
        "20Y": {"code": "DGS20", "name": "20-Year Treasury Yield"},
        "30Y": {"code": "DGS30", "name": "30-Year Treasury Yield"}
    }
    
    # Function to create treasury yield chart with real yield overlay
    def create_treasury_chart(series_code, title):
        try:
            yield_data = fred.get_series(series_code).dropna()
            cpi_inflation = load_cpi_data()
            
            if not yield_data.empty:
                fig = go.Figure()
                
                # Nominal yield
                fig.add_trace(go.Scatter(
                    x=yield_data.index, 
                    y=yield_data.values, 
                    mode='lines', 
                    name=f"{title} (Nominal)",
                    line=dict(color='blue'),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'Date: %{x|%Y-%m-%d}<br>' +
                                  'Yield: %{y:.2f}%<br>' +
                                  '<extra></extra>'
                ))
                
                # Real yield (nominal - inflation)
                if not cpi_inflation.empty:
                    # Align dates and calculate real yield
                    common_dates = yield_data.index.intersection(cpi_inflation.index)
                    if len(common_dates) > 0:
                        real_yield = yield_data.loc[common_dates] - cpi_inflation.loc[common_dates]
                        
                        fig.add_trace(go.Scatter(
                            x=common_dates,
                            y=real_yield.values,
                            mode='lines',
                            name=f"{title} (Real)",
                            line=dict(color='red', dash='dash'),
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                          'Date: %{x|%Y-%m-%d}<br>' +
                                          'Real Yield: %{y:.2f}%<br>' +
                                          '<extra></extra>'
                        ))
                
                fig.update_layout(
                    height=500, 
                    xaxis_title="Date", 
                    yaxis_title="Yield (%)",
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(count=5, label="5Y", step="year", stepmode="backward"),
                                dict(step="all")
                            ])
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    hovermode='x unified',
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                )
                return fig
            else:
                return None
        except Exception as e:
            st.error(f"Error loading {title}: {e}")
            return None
    
    # 3M Treasury
    with subtab1:
        fig = create_treasury_chart("DGS3MO", "3-Month Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 1Y Treasury
    with subtab2:
        fig = create_treasury_chart("DGS1", "1-Year Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 3Y Treasury
    with subtab3:
        fig = create_treasury_chart("DGS3", "3-Year Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 5Y Treasury
    with subtab4:
        fig = create_treasury_chart("DGS5", "5-Year Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 10Y Treasury
    with subtab5:
        fig = create_treasury_chart("DGS10", "10-Year Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 20Y Treasury
    with subtab6:
        fig = create_treasury_chart("DGS20", "20-Year Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 30Y Treasury
    with subtab7:
        fig = create_treasury_chart("DGS30", "30-Year Treasury Yield")
        if fig:
            st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: SPY ETF ---
with tab2:
    st.header(" SPY - S&P 500 ETF (Max Range)")
    try:
        spy = yf.download("SPY", start="2000-01-01", end=pd.Timestamp.today().strftime("%Y-%m-%d"))
        
        # Handle MultiIndex columns by flattening them
        if isinstance(spy.columns, pd.MultiIndex):
            spy.columns = spy.columns.get_level_values(0)
        
        if not spy.empty and "Close" in spy.columns:
            cpi_inflation = load_cpi_data()
            
            fig2 = go.Figure()
            
            # Nominal SPY price
            fig2.add_trace(go.Scatter(
                x=spy.index, 
                y=spy["Close"], 
                mode='lines', 
                name="SPY (Nominal)",
                line=dict(color='blue'),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Date: %{x|%Y-%m-%d}<br>' +
                              'Price: $%{y:.2f}<br>' +
                              '<extra></extra>'
            ))
            
            # Real SPY returns (inflation-adjusted)
            if not cpi_inflation.empty:
                try:
                    # Calculate daily returns for SPY
                    spy_daily_returns = spy["Close"].pct_change().fillna(0)
                    
                    # Get CPI inflation rate (already calculated as YoY % change)
                    # Convert to daily inflation rate
                    cpi_daily_inflation = cpi_inflation.reindex(spy.index, method='ffill').fillna(0) / 365.25 / 100
                    
                    # Calculate real daily returns: (1 + nominal_return) / (1 + inflation_rate) - 1
                    real_daily_returns = (1 + spy_daily_returns) / (1 + cpi_daily_inflation) - 1
                    
                    # Start with initial SPY price and compound with real returns
                    initial_price = spy["Close"].iloc[0]
                    real_spy_price = pd.Series(index=spy.index, dtype=float)
                    real_spy_price.iloc[0] = initial_price
                    
                    # Calculate cumulative real price by compounding real returns
                    cumulative_real_multiplier = (1 + real_daily_returns).cumprod()
                    real_spy_price = initial_price * cumulative_real_multiplier
                    
                    # Remove NaN values
                    real_spy_price = real_spy_price.dropna()
                    
                    fig2.add_trace(go.Scatter(
                        x=real_spy_price.index,
                        y=real_spy_price.values,
                        mode='lines',
                        name="SPY (Real, Inflation-Adjusted)",
                        line=dict(color='red', dash='dash'),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                      'Date: %{x|%Y-%m-%d}<br>' +
                                      'Real Price: $%{y:.2f}<br>' +
                                      '<extra></extra>'
                    ))
                except Exception as e:
                    st.warning(f"Could not calculate real SPY returns: {e}")
            
            fig2.update_layout(
                height=500, 
                xaxis_title="Date", 
                yaxis_title="Price (USD)",
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                hovermode='x unified',
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Add some explanation text
            st.info("💡 **Real vs Nominal SPY**: The real price shows SPY's true purchasing power growth using the formula: Real Return = (1 + Nominal Return) ÷ (1 + Inflation Rate) - 1. This shows what your investment gains were after accounting for inflation.")
            
        else:
            st.warning("⚠️ SPY data not available — please check ticker or date range.")
            st.write("Available columns:", spy.columns.tolist() if not spy.empty else "No data")
    except Exception as e:
        st.error(f"Error downloading SPY data: {e}")

# --- TAB 3: IWM ETF (Russell 2000) ---
with tab3:
    st.header(" IWM - Russell 2000 ETF (Max Range)")
    try:
        iwm = yf.download("IWM", start="2000-01-01", end=pd.Timestamp.today().strftime("%Y-%m-%d"))
        
        # Handle MultiIndex columns by flattening them
        if isinstance(iwm.columns, pd.MultiIndex):
            iwm.columns = iwm.columns.get_level_values(0)
        
        if not iwm.empty and "Close" in iwm.columns:
            cpi_inflation = load_cpi_data()
            
            fig3 = go.Figure()
            
            # Nominal IWM price
            fig3.add_trace(go.Scatter(
                x=iwm.index, 
                y=iwm["Close"], 
                mode='lines', 
                name="IWM (Nominal)",
                line=dict(color='blue'),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Date: %{x|%Y-%m-%d}<br>' +
                              'Price: $%{y:.2f}<br>' +
                              '<extra></extra>'
            ))
            
            # Real IWM returns (inflation-adjusted)
            if not cpi_inflation.empty:
                try:
                    # Calculate daily returns for IWM
                    iwm_daily_returns = iwm["Close"].pct_change().fillna(0)
                    
                    # Get CPI inflation rate (already calculated as YoY % change)
                    # Convert to daily inflation rate
                    cpi_daily_inflation = cpi_inflation.reindex(iwm.index, method='ffill').fillna(0) / 365.25 / 100
                    
                    # Calculate real daily returns: (1 + nominal_return) / (1 + inflation_rate) - 1
                    real_daily_returns = (1 + iwm_daily_returns) / (1 + cpi_daily_inflation) - 1
                    
                    # Start with initial IWM price and compound with real returns
                    initial_price = iwm["Close"].iloc[0]
                    real_iwm_price = pd.Series(index=iwm.index, dtype=float)
                    real_iwm_price.iloc[0] = initial_price
                    
                    # Calculate cumulative real price by compounding real returns
                    cumulative_real_multiplier = (1 + real_daily_returns).cumprod()
                    real_iwm_price = initial_price * cumulative_real_multiplier
                    
                    # Remove NaN values
                    real_iwm_price = real_iwm_price.dropna()
                    
                    fig3.add_trace(go.Scatter(
                        x=real_iwm_price.index,
                        y=real_iwm_price.values,
                        mode='lines',
                        name="IWM (Real, Inflation-Adjusted)",
                        line=dict(color='red', dash='dash'),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                      'Date: %{x|%Y-%m-%d}<br>' +
                                      'Real Price: $%{y:.2f}<br>' +
                                      '<extra></extra>'
                    ))
                except Exception as e:
                    st.warning(f"Could not calculate real IWM returns: {e}")
            
            fig3.update_layout(
                height=500, 
                xaxis_title="Date", 
                yaxis_title="Price (USD)",
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                hovermode='x unified',
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Add some explanation text
            st.info("💡 **Real vs Nominal IWM**: The real price shows IWM's true purchasing power growth after accounting for inflation. This is particularly important for small-cap stocks as they can be more sensitive to economic cycles and inflation.")
            
        else:
            st.warning("⚠️ IWM data not available — please check ticker or date range.")
            st.write("Available columns:", iwm.columns.tolist() if not iwm.empty else "No data")
    except Exception as e:
        st.error(f"Error downloading IWM data: {e}")

# --- TAB 4: UUP ETF (DXY Proxy) ---
with tab4:
    st.header(" Dollar Index (UUP ETF)")
    try:
        uup = yf.download(
            "UUP",
            start="2008-01-01",
            end=pd.Timestamp.today().strftime("%Y-%m-%d")
        )
        
        # Handle MultiIndex columns by flattening them
        if isinstance(uup.columns, pd.MultiIndex):
            uup.columns = uup.columns.get_level_values(0)
        
        if not uup.empty and "Close" in uup.columns:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=uup.index, 
                y=uup["Close"], 
                mode='lines', 
                name="UUP Close",
                hovertemplate='<b>UUP Close</b><br>' +
                              'Date: %{x|%Y-%m-%d}<br>' +
                              'Price: $%{y:.2f}<br>' +
                              '<extra></extra>'
            ))
            fig4.update_layout(
                height=500, 
                xaxis_title="Date", 
                yaxis_title="Price (USD)",
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                hovermode='x unified'
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("⚠️ UUP data not available — please check ticker or date range.")
            st.write("Available columns:", uup.columns.tolist() if not uup.empty else "No data")
    except Exception as e:
        st.error(f"Error downloading UUP data: {e}")

# --- TAB 5: Federal Reserve Data ---
with tab5:
    st.header("Federal Reserve Data")
    
    # Sub-tabs for different Fed data
    fed_subtab1, fed_subtab2, fed_subtab3 = st.tabs(["Temporary Repo Operations", "Standing Repo Facility", "Reverse Repo Facility"])
    
    # Temporary Open Market Operations Repo (RPONTSYD)
    with fed_subtab1:
        st.subheader("Temporary Open Market Operations - Repo Facility")
        try:
            # FRED series code for temporary repo operations (banks borrowing from Fed)
            repo_data = fred.get_series("RPONTSYD", start="2000-01-01").dropna()
            
            if not repo_data.empty:
                fig_repo = go.Figure()
                
                fig_repo.add_trace(go.Scatter(
                    x=repo_data.index,
                    y=repo_data.values,
                    mode='lines',
                    name="Temporary Repo Operations",
                    line=dict(color='darkblue'),
                    hovertemplate='<b>Temporary Repo Operations</b><br>' +
                                  'Date: %{x|%Y-%m-%d}<br>' +
                                  'Amount: $%{y:,.0f} billions<br>' +
                                  '<extra></extra>'
                ))
                
                fig_repo.update_layout(
                    height=500,
                    xaxis_title="Date",
                    yaxis_title="Amount (Billions USD)",
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(count=5, label="5Y", step="year", stepmode="backward"),
                                dict(step="all")
                            ])
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_repo, use_container_width=True)
                
                # Add explanation
                st.info("💡 **Temporary Open Market Operations**: This shows Treasury securities purchased by the Fed in temporary open market operations. These were used extensively during QE periods (2008-2014, 2020-2021) to provide liquidity to the banking system. This is different from the Standing Repo Facility introduced in 2021.")
                
                # Add brief description
                st.markdown("""
                **Quick Reference:**
                - **Purpose**: Emergency liquidity tool used during financial crises
                - **When**: Active during 2008-2014 and 2020-2021 QE periods
                - **Direction**: Fed lends cash to banks, receives Treasury collateral
                - **Signal**: High usage = Financial system stress, banks need Fed funding
                """)
                
            else:
                st.warning("⚠️ Temporary repo data not available")
                
        except Exception as e:
            st.error(f"Error loading temporary repo data: {e}")
    
    # Standing Repo Facility (SRF) - Introduced July 2021
    with fed_subtab2:
        st.subheader("Standing Repo Facility (SRF)")
        try:
            # Try to get SRF data - this might not be available in FRED yet
            # You might need to find the correct series code or use alternative data source
            
            # For now, let's try a few potential series codes
            srf_series_codes = ["SRFUTILIZATION", "SRFAMOUNT", "RPONTSYSRF"]  # These are guesses
            srf_data = None
            
            for code in srf_series_codes:
                try:
                    srf_data = fred.get_series(code, start="2021-07-01").dropna()
                    if not srf_data.empty:
                        break
                except:
                    continue
            
            if srf_data is not None and not srf_data.empty:
                fig_srf = go.Figure()
                
                fig_srf.add_trace(go.Scatter(
                    x=srf_data.index,
                    y=srf_data.values,
                    mode='lines',
                    name="Standing Repo Facility",
                    line=dict(color='green'),
                    hovertemplate='<b>Standing Repo Facility</b><br>' +
                                  'Date: %{x|%Y-%m-%d}<br>' +
                                  'Amount: $%{y:,.0f} billions<br>' +
                                  '<extra></extra>'
                ))
                
                fig_srf.update_layout(
                    height=500,
                    xaxis_title="Date",
                    yaxis_title="Amount (Billions USD)",
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(count=2, label="2Y", step="year", stepmode="backward"),
                                dict(step="all")
                            ])
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_srf, use_container_width=True)
                
                # Add explanation
                st.info("💡 **Standing Repo Facility (SRF)**: Introduced in July 2021, this facility serves as a backstop in money markets. Banks can borrow against Treasury and agency securities at a rate set by the FOMC. Higher usage indicates funding stress in short-term markets.")
                
                # Add brief description
                st.markdown("""
                **Quick Reference:**
                - **Purpose**: Permanent backstop for money market functioning
                - **When**: Available daily since July 2021
                - **Direction**: Banks can borrow cash from Fed using Treasury/agency collateral
                - **Signal**: Usage indicates short-term funding market stress
                """)
                
            else:
                st.warning("⚠️ Standing Repo Facility data not available in FRED")
                st.info("💡 **Standing Repo Facility (SRF)**: This facility was introduced in July 2021 as a backstop for money markets. Data may not be available in FRED yet, or may require direct access to NY Fed data.")
                
                # Add brief description even when no data
                st.markdown("""
                **Quick Reference:**
                - **Purpose**: Permanent backstop for money market functioning
                - **When**: Available daily since July 2021
                - **Direction**: Banks can borrow cash from Fed using Treasury/agency collateral
                - **Signal**: Usage indicates short-term funding market stress
                """)
                
        except Exception as e:
            st.error(f"Error loading Standing Repo Facility data: {e}")
            st.info("💡 **Standing Repo Facility (SRF)**: This facility was introduced in July 2021 as a backstop for money markets. Data may not be available in FRED yet.")
            
            # Add brief description even when error
            st.markdown("""
            **Quick Reference:**
            - **Purpose**: Permanent backstop for money market functioning
            - **When**: Available daily since July 2021
            - **Direction**: Banks can borrow cash from Fed using Treasury/agency collateral
            - **Signal**: Usage indicates short-term funding market stress
            """)
    
    # Reverse Repo Facility (RRPONTSYD)
    with fed_subtab3:
        st.subheader("Overnight Reverse Repurchase Agreement Facility")
        try:
            # FRED series code for reverse repo facility
            reverse_repo_data = fred.get_series("RRPONTSYD", start="2013-01-01").dropna()
            
            if not reverse_repo_data.empty:
                fig_reverse_repo = go.Figure()
                
                fig_reverse_repo.add_trace(go.Scatter(
                    x=reverse_repo_data.index,
                    y=reverse_repo_data.values,
                    mode='lines',
                    name="Reverse Repo Facility",
                    line=dict(color='darkgreen'),
                    hovertemplate='<b>Reverse Repo Facility</b><br>' +
                                  'Date: %{x|%Y-%m-%d}<br>' +
                                  'Amount: $%{y:,.0f} billions<br>' +
                                  '<extra></extra>'
                ))
                
                fig_reverse_repo.update_layout(
                    height=500,
                    xaxis_title="Date",
                    yaxis_title="Amount (Billions USD)",
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(count=5, label="5Y", step="year", stepmode="backward"),
                                dict(step="all")
                            ])
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_reverse_repo, use_container_width=True)
                
                # Add explanation
                st.info("💡 **Reverse Repo Facility**: This shows daily usage where institutions park cash WITH the Fed overnight. Higher usage indicates excess liquidity in the financial system, as institutions have more cash than profitable investment opportunities.")
                
                # Add brief description
                st.markdown("""
                **Quick Reference:**
                - **Purpose**: Absorb excess liquidity from financial system
                - **When**: Available daily since 2013 (expanded use since 2021)
                - **Direction**: Banks/money markets lend cash TO Fed, receive Treasury collateral
                - **Signal**: High usage = Too much cash in system, limited investment options
                """)
                
            else:
                st.warning("⚠️ Reverse Repo data not available")
                
        except Exception as e:
            st.error(f"Error loading Reverse Repo data: {e}")

# --- TAB 6: VIX Index ---
with tab6:
    st.header("VIX - Volatility Index")
    try:
        # Download VIX data using yfinance
        vix = yf.download("^VIX", start="2000-01-01", end=pd.Timestamp.today().strftime("%Y-%m-%d"))
        
        # Handle MultiIndex columns by flattening them
        if isinstance(vix.columns, pd.MultiIndex):
            vix.columns = vix.columns.get_level_values(0)
        
        if not vix.empty and "Close" in vix.columns:
            fig_vix = go.Figure()
            
            # VIX close price
            fig_vix.add_trace(go.Scatter(
                x=vix.index,
                y=vix["Close"],
                mode='lines',
                name="VIX Close",
                line=dict(color='orange'),
                hovertemplate='<b>VIX Close</b><br>' +
                              'Date: %{x|%Y-%m-%d}<br>' +
                              'VIX: %{y:.2f}<br>' +
                              '<extra></extra>'
            ))
            
            # Add horizontal lines for key VIX levels
            fig_vix.add_hline(y=20, line_dash="dash", line_color="red", 
                             annotation_text="High Volatility (20)", annotation_position="bottom right")
            fig_vix.add_hline(y=30, line_dash="dash", line_color="darkred", 
                             annotation_text="Very High Volatility (30)", annotation_position="bottom right")
            
            fig_vix.update_layout(
                height=500,
                xaxis_title="Date",
                yaxis_title="VIX Level",
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_vix, use_container_width=True)
            
            # Add explanation
            st.info("💡 **VIX Interpretation**: VIX below 20 = Low volatility/complacency, 20-30 = Elevated volatility, Above 30 = High fear/uncertainty. The VIX is often called the 'fear index' as it spikes during market stress.")
            
            # Add current VIX level info
            current_vix = vix["Close"].iloc[-1]
            if current_vix < 20:
                vix_interpretation = "🟢 Low Volatility"
            elif current_vix < 30:
                vix_interpretation = "🟡 Elevated Volatility"
            else:
                vix_interpretation = "🔴 High Volatility"
            
            st.metric(label="Latest VIX Level", value=f"{current_vix:.2f}", help=vix_interpretation)
            
        else:
            st.warning("⚠️ VIX data not available — please check ticker or date range.")
            st.write("Available columns:", vix.columns.tolist() if not vix.empty else "No data")
            
    except Exception as e:
        st.error(f"Error downloading VIX data: {e}")