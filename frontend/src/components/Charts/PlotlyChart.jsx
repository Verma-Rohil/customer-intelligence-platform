import ReactPlotly from 'react-plotly.js';
const Plot = ReactPlotly.default || ReactPlotly;

/**
 * Reusable Plotly chart wrapper with dark theme defaults.
 * Spreads any additional layout/config props.
 */
export default function PlotlyChart({ data, layout = {}, config = {}, style = {} }) {
  const defaultLayout = {
    template: 'plotly_white',
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: "'Outfit', sans-serif",
      color: '#475569',
    },
    margin: { t: 40, r: 20, b: 40, l: 60 },
    ...layout,
  };

  const defaultConfig = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    responsive: true,
    ...config,
  };

  return (
    <Plot
      data={data}
      layout={defaultLayout}
      config={defaultConfig}
      useResizeHandler
      style={{ width: '100%', height: '100%', ...style }}
    />
  );
}
