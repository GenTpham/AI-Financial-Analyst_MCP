"""
Visualization Agent - Tạo biểu đồ và trực quan hóa dữ liệu tài chính
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from pathlib import Path

class VisualizationAgent:
    """Agent chịu trách nhiệm tạo biểu đồ và trực quan hóa"""
    
    def __init__(self, config: Dict[str, Any], output_config: Dict[str, Any]):
        self.config = config
        self.output_config = output_config
        self.logger = logging.getLogger(__name__)
        
        # Output settings
        self.charts_directory = Path(output_config.get('charts_directory', './output/charts'))
        self.default_format = output_config.get('default_chart_format', 'html')
        
        # Create charts directory if it doesn't exist
        self.charts_directory.mkdir(parents=True, exist_ok=True)
        
        # Chart styling
        self.setup_styling()
    
    def setup_styling(self):
        """Setup chart styling"""
        # Plotly theme
        self.plotly_theme = "plotly_white"
        
        # Color palette
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'bull': '#26a69a',
            'bear': '#ef5350'
        }
        
        # Matplotlib styling
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    async def create_visualization(
        self,
        data: Dict[str, Any],
        chart_type: str,
        title: str = None,
        save_path: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create visualization based on chart type
        
        Args:
            data: Data to visualize
            chart_type: Type of chart to create
            title: Chart title
            save_path: Path to save the chart
            **kwargs: Additional parameters
        
        Returns:
            Dict containing chart information and path
        """
        try:
            # Generate default title if not provided
            if title is None:
                title = f"{chart_type.replace('_', ' ').title()} Chart"
            
            # Generate save path if not provided
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = self.charts_directory / f"{chart_type}_{timestamp}.{self.default_format}"
            else:
                save_path = Path(save_path)
            
            # Create chart based on type
            if chart_type == "line":
                result = await self._create_line_chart(data, title, save_path, **kwargs)
            elif chart_type == "candlestick":
                result = await self._create_candlestick_chart(data, title, save_path, **kwargs)
            elif chart_type == "bar":
                result = await self._create_bar_chart(data, title, save_path, **kwargs)
            elif chart_type == "heatmap":
                result = await self._create_heatmap(data, title, save_path, **kwargs)
            elif chart_type == "dashboard":
                result = await self._create_dashboard(data, title, save_path, **kwargs)
            elif chart_type == "correlation":
                result = await self._create_correlation_matrix(data, title, save_path, **kwargs)
            elif chart_type == "technical":
                result = await self._create_technical_chart(data, title, save_path, **kwargs)
            elif chart_type == "volume":
                result = await self._create_volume_chart(data, title, save_path, **kwargs)
            elif chart_type == "returns":
                result = await self._create_returns_chart(data, title, save_path, **kwargs)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            self.logger.info(f"Created {chart_type} chart: {save_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating {chart_type} chart: {e}")
            raise
    
    async def _create_line_chart(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create line chart"""
        try:
            # Extract data
            if 'historical' in data:
                df = pd.DataFrame(data['historical'])
            else:
                df = pd.DataFrame(data)
            
            # Create figure
            fig = go.Figure()
            
            # Add close price line
            if 'Close' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else df.get('Date', range(len(df))),
                    y=df['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color=self.colors['primary'], width=2)
                ))
            
            # Add moving averages if available
            if 'sma_20' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else df.get('Date', range(len(df))),
                    y=df['sma_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color=self.colors['secondary'], width=1)
                ))
            
            if 'sma_50' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else df.get('Date', range(len(df))),
                    y=df['sma_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color=self.colors['success'], width=1)
                ))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Price",
                template=self.plotly_theme,
                hovermode='x unified'
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'line',
                'title': title,
                'save_path': str(save_path),
                'data_points': len(df),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating line chart: {e}")
    
    async def _create_candlestick_chart(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create candlestick chart"""
        try:
            # Extract data with proper structure handling
            if 'data' in data and 'historical' in data['data']:
                df = pd.DataFrame(data['data']['historical'])
            elif 'historical' in data:
                df = pd.DataFrame(data['historical'])
            else:
                df = pd.DataFrame(data)
            
            # Check if DataFrame is empty
            if df.empty:
                raise ValueError("No data available for candlestick chart")
            
            # Ensure we have OHLC data
            required_columns = ['Open', 'High', 'Low', 'Close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Try to create a simple line chart instead
                self.logger.warning(f"Missing OHLC columns {missing_columns}, creating line chart instead")
                return await self._create_line_chart(data, title, save_path, **kwargs)
            
            # Ensure we have Volume column, create dummy if missing
            if 'Volume' not in df.columns:
                df['Volume'] = 0
                self.logger.warning("Volume column missing, using dummy values")
            
            # Handle date index
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            elif not isinstance(df.index, pd.DatetimeIndex):
                # Create a date range if no date column
                df.index = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_width=[0.7, 0.3],
                subplot_titles=('Price', 'Volume')
            )
            
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else df.get('Date', range(len(df))),
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='OHLC',
                    increasing_line_color=self.colors['bull'],
                    decreasing_line_color=self.colors['bear']
                ),
                row=1, col=1
            )
            
            # Add volume bars if available
            if 'Volume' in df.columns:
                fig.add_trace(
                    go.Bar(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df.get('Date', range(len(df))),
                        y=df['Volume'],
                        name='Volume',
                        marker_color=self.colors['info'],
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            # Update layout
            fig.update_layout(
                title=title,
                template=self.plotly_theme,
                xaxis_rangeslider_visible=False,
                showlegend=True
            )
            
            # Update y-axes
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'candlestick',
                'title': title,
                'save_path': str(save_path),
                'data_points': len(df),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating candlestick chart: {e}")
    
    async def _create_technical_chart(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create technical analysis chart with indicators"""
        try:
            # Extract data and technical indicators
            if 'historical' in data:
                df = pd.DataFrame(data['historical'])
            else:
                df = pd.DataFrame(data)
            
            technical_data = data.get('technical_analysis', {})
            
            # Create subplots for price, volume, and indicators
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                row_heights=[0.5, 0.15, 0.15, 0.2],
                subplot_titles=('Price & Moving Averages', 'Volume', 'RSI', 'MACD')
            )
            
            # Price and Moving Averages
            fig.add_trace(
                go.Candlestick(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price',
                    increasing_line_color=self.colors['bull'],
                    decreasing_line_color=self.colors['bear']
                ),
                row=1, col=1
            )
            
            # Moving Averages
            ma_data = technical_data.get('moving_averages', {})
            for ma_name, ma_info in ma_data.items():
                if ma_info.get('values'):
                    fig.add_trace(
                        go.Scatter(
                            x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                            y=ma_info['values'],
                            mode='lines',
                            name=ma_name.upper(),
                            line=dict(width=1)
                        ),
                        row=1, col=1
                    )
            
            # Bollinger Bands
            bb_data = technical_data.get('bollinger_bands', {})
            if bb_data:
                fig.add_trace(
                    go.Scatter(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                        y=bb_data.get('upper', []),
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='rgba(173, 204, 255, 0.5)', width=1)
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                        y=bb_data.get('lower', []),
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='rgba(173, 204, 255, 0.5)', width=1),
                        fill='tonexty'
                    ),
                    row=1, col=1
                )
            
            # Volume
            if 'Volume' in df.columns:
                fig.add_trace(
                    go.Bar(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                        y=df['Volume'],
                        name='Volume',
                        marker_color=self.colors['info'],
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            # RSI
            rsi_data = technical_data.get('rsi', {})
            if rsi_data.get('values'):
                fig.add_trace(
                    go.Scatter(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                        y=rsi_data['values'],
                        mode='lines',
                        name='RSI',
                        line=dict(color=self.colors['warning'])
                    ),
                    row=3, col=1
                )
                
                # RSI levels
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
                fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
            
            # MACD
            macd_data = technical_data.get('macd', {})
            if macd_data:
                # MACD line
                if macd_data.get('macd'):
                    fig.add_trace(
                        go.Scatter(
                            x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                            y=macd_data['macd'],
                            mode='lines',
                            name='MACD',
                            line=dict(color=self.colors['primary'])
                        ),
                        row=4, col=1
                    )
                
                # Signal line
                if macd_data.get('signal'):
                    fig.add_trace(
                        go.Scatter(
                            x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                            y=macd_data['signal'],
                            mode='lines',
                            name='Signal',
                            line=dict(color=self.colors['secondary'])
                        ),
                        row=4, col=1
                    )
                
                # Histogram
                if macd_data.get('histogram'):
                    fig.add_trace(
                        go.Bar(
                            x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                            y=macd_data['histogram'],
                            name='Histogram',
                            marker_color=self.colors['success'],
                            opacity=0.7
                        ),
                        row=4, col=1
                    )
            
            # Update layout
            fig.update_layout(
                title=title,
                template=self.plotly_theme,
                xaxis_rangeslider_visible=False,
                showlegend=True,
                height=800
            )
            
            # Update y-axes
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
            fig.update_yaxes(title_text="MACD", row=4, col=1)
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'technical',
                'title': title,
                'save_path': str(save_path),
                'data_points': len(df),
                'indicators': list(technical_data.keys()),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating technical chart: {e}")
    
    async def _create_dashboard(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create comprehensive dashboard"""
        try:
            # Create subplots for dashboard
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=('Price Chart', 'Volume Analysis', 'Technical Indicators', 'Risk Metrics', 'Performance', 'Market Comparison'),
                specs=[[{"secondary_y": True}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "indicator"}],
                       [{"type": "scatter"}, {"type": "bar"}]]
            )
            
            # Extract data
            if 'historical' in data:
                df = pd.DataFrame(data['historical'])
            else:
                df = pd.DataFrame(data)
            
            # Price chart (row 1, col 1)
            fig.add_trace(
                go.Scatter(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                    y=df['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color=self.colors['primary'])
                ),
                row=1, col=1
            )
            
            # Volume chart (row 1, col 2)
            if 'Volume' in df.columns:
                fig.add_trace(
                    go.Bar(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                        y=df['Volume'],
                        name='Volume',
                        marker_color=self.colors['info']
                    ),
                    row=1, col=2
                )
            
            # Technical indicators (row 2, col 1)
            technical_data = data.get('technical_analysis', {})
            rsi_data = technical_data.get('rsi', {})
            if rsi_data.get('values'):
                fig.add_trace(
                    go.Scatter(
                        x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                        y=rsi_data['values'],
                        mode='lines',
                        name='RSI',
                        line=dict(color=self.colors['warning'])
                    ),
                    row=2, col=1
                )
            
            # Risk metrics (row 2, col 2)
            risk_data = data.get('risk_analysis', {})
            if risk_data:
                sharpe_ratio = risk_data.get('sharpe_ratio', 0)
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=sharpe_ratio,
                        title={"text": "Sharpe Ratio"},
                        gauge={"axis": {"range": [-2, 3]},
                               "bar": {"color": "darkblue"},
                               "steps": [{"range": [-2, 0], "color": "lightgray"},
                                        {"range": [0, 1], "color": "gray"},
                                        {"range": [1, 3], "color": "lightgreen"}],
                               "threshold": {"line": {"color": "red", "width": 4},
                                           "thickness": 0.75, "value": 1}}
                    ),
                    row=2, col=2
                )
            
            # Performance metrics (row 3, col 1)
            price_data = data.get('price_analysis', {})
            if price_data:
                returns = [
                    price_data.get('price_changes', {}).get('1_day', 0),
                    price_data.get('price_changes', {}).get('20_day', 0)
                ]
                periods = ['1 Day', '20 Days']
                
                fig.add_trace(
                    go.Bar(
                        x=periods,
                        y=returns,
                        name='Returns (%)',
                        marker_color=[self.colors['bull'] if r > 0 else self.colors['bear'] for r in returns]
                    ),
                    row=3, col=1
                )
            
            # Update layout
            fig.update_layout(
                title=title,
                template=self.plotly_theme,
                showlegend=True,
                height=900
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'dashboard',
                'title': title,
                'save_path': str(save_path),
                'data_points': len(df),
                'sections': ['price', 'volume', 'technical', 'risk', 'performance', 'comparison'],
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating dashboard: {e}")
    
    async def _create_correlation_matrix(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create correlation matrix heatmap"""
        try:
            # Handle different data formats
            if 'correlation_matrix' in data:
                corr_data = data['correlation_matrix']
                df_corr = pd.DataFrame(corr_data)
            elif isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
                # Multiple stocks data
                prices = {}
                for symbol, stock_data in data.items():
                    if 'historical' in stock_data:
                        hist_df = pd.DataFrame(stock_data['historical'])
                        if 'Close' in hist_df.columns:
                            prices[symbol] = hist_df['Close']
                
                if prices:
                    df_prices = pd.DataFrame(prices)
                    df_corr = df_prices.corr()
                else:
                    raise ValueError("No price data found for correlation")
            else:
                raise ValueError("Invalid data format for correlation matrix")
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=df_corr.values,
                x=df_corr.columns,
                y=df_corr.index,
                colorscale='RdBu',
                zmid=0,
                text=df_corr.round(3).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=title,
                template=self.plotly_theme,
                xaxis_title="Symbols",
                yaxis_title="Symbols"
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'correlation',
                'title': title,
                'save_path': str(save_path),
                'symbols': list(df_corr.columns),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating correlation matrix: {e}")
    
    async def _create_bar_chart(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create bar chart"""
        try:
            # Simple bar chart implementation
            fig = go.Figure()
            
            if isinstance(data, dict):
                x_values = list(data.keys())
                y_values = list(data.values())
                
                fig.add_trace(go.Bar(
                    x=x_values,
                    y=y_values,
                    marker_color=self.colors['primary']
                ))
            
            fig.update_layout(
                title=title,
                template=self.plotly_theme
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'bar',
                'title': title,
                'save_path': str(save_path),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating bar chart: {e}")
    
    async def _create_heatmap(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create heatmap"""
        try:
            # Convert data to DataFrame if needed
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=df.values,
                x=df.columns,
                y=df.index,
                colorscale='Viridis'
            ))
            
            fig.update_layout(
                title=title,
                template=self.plotly_theme
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'heatmap',
                'title': title,
                'save_path': str(save_path),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating heatmap: {e}")
    
    async def _create_volume_chart(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create volume chart"""
        try:
            if 'historical' in data:
                df = pd.DataFrame(data['historical'])
            else:
                df = pd.DataFrame(data)
            
            fig = go.Figure()
            
            if 'Volume' in df.columns:
                fig.add_trace(go.Bar(
                    x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                    y=df['Volume'],
                    name='Volume',
                    marker_color=self.colors['info']
                ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Volume",
                template=self.plotly_theme
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'volume',
                'title': title,
                'save_path': str(save_path),
                'data_points': len(df),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating volume chart: {e}")
    
    async def _create_returns_chart(self, data: Dict[str, Any], title: str, save_path: Path, **kwargs) -> Dict[str, Any]:
        """Create returns chart"""
        try:
            if 'historical' in data:
                df = pd.DataFrame(data['historical'])
            else:
                df = pd.DataFrame(data)
            
            # Calculate returns
            df['returns'] = df['Close'].pct_change()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df.index if isinstance(df.index, pd.DatetimeIndex) else range(len(df)),
                y=df['returns'],
                mode='lines',
                name='Returns',
                line=dict(color=self.colors['primary'])
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Returns",
                template=self.plotly_theme
            )
            
            # Save chart
            if save_path.suffix == '.html':
                fig.write_html(str(save_path))
            elif save_path.suffix == '.png':
                fig.write_image(str(save_path))
            
            return {
                'chart_type': 'returns',
                'title': title,
                'save_path': str(save_path),
                'data_points': len(df),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error creating returns chart: {e}")
    
    async def create_multi_chart(self, charts_data: List[Dict[str, Any]], title: str = "Multi-Chart Dashboard") -> Dict[str, Any]:
        """Create multiple charts in one dashboard"""
        try:
            results = []
            
            for i, chart_data in enumerate(charts_data):
                chart_type = chart_data.get('type', 'line')
                data = chart_data.get('data', {})
                chart_title = chart_data.get('title', f'Chart {i+1}')
                
                result = await self.create_visualization(
                    data=data,
                    chart_type=chart_type,
                    title=chart_title
                )
                results.append(result)
            
            return {
                'dashboard_title': title,
                'charts': results,
                'total_charts': len(results),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating multi-chart dashboard: {e}")
            raise 