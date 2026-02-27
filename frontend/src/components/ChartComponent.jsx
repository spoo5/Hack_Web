import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./ChartComponent.css";

const COLORS = {
  primary: "#EAAB00",
  secondary: "#FFC94D",
  tertiary: "#FFD700",
  quaternary: "#FFED4E",
  success: "#4ECDC4",
  error: "#FF6B6B",
};

const ChartComponent = ({ type, data }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="chart-placeholder">
        <p className="text-muted">No visualization data available</p>
      </div>
    );
  }

  // KPI Card (single metric)
  if (type === "kpi") {
    return (
      <div className="kpi-card">
        <div className="kpi-value">{data.value?.toLocaleString()}</div>
        <div className="kpi-label">Result</div>
      </div>
    );
  }

  // Bar Chart
  if (type === "bar") {
    const chartData =
      data.labels?.map((label, idx) => ({
        name: label,
        value: data.datasets?.[0]?.data[idx] || 0,
      })) || [];

    return (
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(234, 171, 0, 0.1)"
            />
            <XAxis
              dataKey="name"
              stroke="#B4B8C5"
              angle={-45}
              textAnchor="end"
              height={100}
              style={{ fontSize: "14px" }}
            />
            <YAxis stroke="#B4B8C5" style={{ fontSize: "14px" }} />
            <Tooltip
              contentStyle={{
                background: "#1A1D2B",
                border: "1px solid rgba(234, 171, 0, 0.3)",
                borderRadius: "8px",
                color: "#FFFFFF",
              }}
            />
            <Legend wrapperStyle={{ paddingTop: "20px" }} />
            <Bar
              dataKey="value"
              fill={COLORS.primary}
              radius={[8, 8, 0, 0]}
              name={data.datasets?.[0]?.label || "Value"}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // Pie Chart
  if (type === "pie" || type === "doughnut") {
    const chartData =
      data.labels?.map((label, idx) => ({
        name: label,
        value: data.datasets?.[0]?.data[idx] || 0,
      })) || [];

    const colorPalette = [
      COLORS.primary,
      COLORS.secondary,
      COLORS.tertiary,
      COLORS.success,
      COLORS.error,
    ];

    return (
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={true}
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(1)}%`
              }
              outerRadius={type === "doughnut" ? 120 : 140}
              innerRadius={type === "doughnut" ? 80 : 0}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={colorPalette[index % colorPalette.length]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#1A1D2B",
                border: "1px solid rgba(234, 171, 0, 0.3)",
                borderRadius: "8px",
                color: "#FFFFFF",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // Line Chart
  if (type === "line") {
    const chartData =
      data.labels?.map((label, idx) => ({
        name: label,
        value: data.datasets?.[0]?.data[idx] || 0,
      })) || [];

    return (
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(234, 171, 0, 0.1)"
            />
            <XAxis
              dataKey="name"
              stroke="#B4B8C5"
              angle={-45}
              textAnchor="end"
              height={100}
              style={{ fontSize: "14px" }}
            />
            <YAxis stroke="#B4B8C5" style={{ fontSize: "14px" }} />
            <Tooltip
              contentStyle={{
                background: "#1A1D2B",
                border: "1px solid rgba(234, 171, 0, 0.3)",
                borderRadius: "8px",
                color: "#FFFFFF",
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              stroke={COLORS.primary}
              strokeWidth={3}
              dot={{ fill: COLORS.primary, r: 6 }}
              activeDot={{ r: 8 }}
              name={data.datasets?.[0]?.label || "Value"}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // None/Unknown
  return (
    <div className="chart-placeholder">
      <p className="text-muted">Visualization type "{type}" not supported</p>
    </div>
  );
};

export default ChartComponent;
