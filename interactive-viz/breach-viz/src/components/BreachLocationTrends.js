import React, { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

const BreachLocationTrends = () => {
  const [chartType, setChartType] = useState('absolute');

  // Data showing breach counts by location over time
  const locationTrendsData = [
    { year: 2015, "Network Server": 11, "Email": 15, "Electronic Medical Record": 9, "Paper/Films": 17, "Other": 9, "Desktop Computer": 4, "Total": 65 },
    { year: 2016, "Network Server": 65, "Email": 30, "Electronic Medical Record": 18, "Paper/Films": 25, "Other": 40, "Desktop Computer": 12, "Total": 190 },
    { year: 2017, "Network Server": 65, "Email": 65, "Electronic Medical Record": 21, "Paper/Films": 14, "Other": 40, "Desktop Computer": 5, "Total": 210 },
    { year: 2018, "Network Server": 48, "Email": 80, "Electronic Medical Record": 14, "Paper/Films": 26, "Other": 38, "Desktop Computer": 8, "Total": 214 },
    { year: 2019, "Network Server": 97, "Email": 149, "Electronic Medical Record": 18, "Paper/Films": 20, "Other": 50, "Desktop Computer": 9, "Total": 343 },
    { year: 2020, "Network Server": 199, "Email": 167, "Electronic Medical Record": 22, "Paper/Films": 24, "Other": 40, "Desktop Computer": 3, "Total": 455 },
    { year: 2021, "Network Server": 264, "Email": 155, "Electronic Medical Record": 24, "Paper/Films": 9, "Other": 28, "Desktop Computer": 2, "Total": 482 },
    { year: 2022, "Network Server": 258, "Email": 137, "Electronic Medical Record": 53, "Paper/Films": 6, "Other": 18, "Desktop Computer": 3, "Total": 475 },
    { year: 2023, "Network Server": 302, "Email": 104, "Electronic Medical Record": 19, "Paper/Films": 13, "Other": 10, "Desktop Computer": 2, "Total": 450 },
    { year: 2024, "Network Server": 330, "Email": 134, "Electronic Medical Record": 17, "Paper/Films": 12, "Other": 21, "Desktop Computer": 3, "Total": 517 },
    { year: 2025, "Network Server": 111, "Email": 42, "Electronic Medical Record": 8, "Paper/Films": 4, "Other": 8, "Desktop Computer": 0, "Total": 173 }
  ];

  // Data showing percentage distribution by location over time
  const percentageDistributionData = [
    { year: 2015, "Network Server (%)": 16.9, "Email (%)": 23.1, "Electronic Medical Record (%)": 13.8, "Paper/Films (%)": 26.2, "Other (%)": 13.8, "Desktop Computer (%)": 6.2 },
    { year: 2016, "Network Server (%)": 34.2, "Email (%)": 15.8, "Electronic Medical Record (%)": 9.5, "Paper/Films (%)": 13.2, "Other (%)": 21.1, "Desktop Computer (%)": 6.3 },
    { year: 2017, "Network Server (%)": 31.0, "Email (%)": 31.0, "Electronic Medical Record (%)": 10.0, "Paper/Films (%)": 6.7, "Other (%)": 19.0, "Desktop Computer (%)": 2.4 },
    { year: 2018, "Network Server (%)": 22.4, "Email (%)": 37.4, "Electronic Medical Record (%)": 6.5, "Paper/Films (%)": 12.1, "Other (%)": 17.8, "Desktop Computer (%)": 3.7 },
    { year: 2019, "Network Server (%)": 28.3, "Email (%)": 43.4, "Electronic Medical Record (%)": 5.2, "Paper/Films (%)": 5.8, "Other (%)": 14.6, "Desktop Computer (%)": 2.6 },
    { year: 2020, "Network Server (%)": 43.7, "Email (%)": 36.7, "Electronic Medical Record (%)": 4.8, "Paper/Films (%)": 5.3, "Other (%)": 8.8, "Desktop Computer (%)": 0.7 },
    { year: 2021, "Network Server (%)": 54.8, "Email (%)": 32.2, "Electronic Medical Record (%)": 5.0, "Paper/Films (%)": 1.9, "Other (%)": 5.8, "Desktop Computer (%)": 0.4 },
    { year: 2022, "Network Server (%)": 54.3, "Email (%)": 28.8, "Electronic Medical Record (%)": 11.2, "Paper/Films (%)": 1.3, "Other (%)": 3.8, "Desktop Computer (%)": 0.6 },
    { year: 2023, "Network Server (%)": 67.1, "Email (%)": 23.1, "Electronic Medical Record (%)": 4.2, "Paper/Films (%)": 2.9, "Other (%)": 2.2, "Desktop Computer (%)": 0.4 },
    { year: 2024, "Network Server (%)": 63.8, "Email (%)": 25.9, "Electronic Medical Record (%)": 3.3, "Paper/Films (%)": 2.3, "Other (%)": 4.1, "Desktop Computer (%)": 0.6 },
    { year: 2025, "Network Server (%)": 64.2, "Email (%)": 24.3, "Electronic Medical Record (%)": 4.6, "Paper/Films (%)": 2.3, "Other (%)": 4.6, "Desktop Computer (%)": 0.0 }
  ];

  // Annual growth rate data for Network Server breaches (the dominant location)
  const networkServerGrowthData = locationTrendsData.map((item, index, array) => {
    if (index === 0) return { year: item.year, growth: 0 };
    
    const prevYear = array[index - 1];
    const growthRate = prevYear["Network Server"] > 0 
      ? ((item["Network Server"] - prevYear["Network Server"]) / prevYear["Network Server"] * 100).toFixed(1)
      : 0;
      
    return { 
      year: item.year, 
      growth: parseFloat(growthRate)
    };
  }).filter(item => item.year < 2025); // Exclude 2025 as it's incomplete

  // Top breach locations with their CAGR (2015-2024)
  const locationGrowthRates = [
    { name: "Network Server", cagr: 45.92 },
    { name: "Email", cagr: 27.55 },
    { name: "Electronic Medical Record", cagr: 7.32 },
    { name: "Other", cagr: 9.87 },
    { name: "Paper/Films", cagr: -3.80 },
    { name: "Desktop Computer", cagr: -3.15 }
  ].sort((a, b) => b.cagr - a.cagr);

  // Color scheme for the charts
  const COLORS = {
    "Network Server": "#8884d8",
    "Email": "#82ca9d",
    "Electronic Medical Record": "#ffc658",
    "Paper/Films": "#ff8042",
    "Other": "#a4de6c",
    "Desktop Computer": "#d0ed57"
  };

  // Custom tooltip for the charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="p-3 bg-white border border-gray-200 rounded-md shadow-md">
          <p className="font-bold">{`Year: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={`item-${index}`} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}${entry.name.includes('%') ? '%' : entry.name === 'growth' ? '%' : ''}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="flex flex-col items-center">
      <h1 className="text-2xl font-bold mb-4">Healthcare Data Breach Trends by System Location (2015-2025)</h1>
      
      <div className="mb-4">
        <select 
          className="px-4 py-2 border border-gray-300 rounded-md bg-white"
          value={chartType}
          onChange={(e) => setChartType(e.target.value)}
        >
          <option value="absolute">Absolute Numbers</option>
          <option value="percentage">Percentage Distribution</option>
          <option value="stacked">Stacked View</option>
          <option value="networkServerGrowth">Network Server Growth Rate</option>
          <option value="growthComparison">Location Growth Comparison</option>
        </select>
      </div>

      <div className="w-full max-w-5xl p-4 bg-white rounded-lg shadow">
        {chartType === 'absolute' && (
          <>
            <h2 className="text-xl font-semibold mb-2">Absolute Number of Breaches by System Location</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={locationTrendsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line type="monotone" dataKey="Network Server" stroke={COLORS["Network Server"]} strokeWidth={3} activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="Email" stroke={COLORS["Email"]} strokeWidth={3} activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="Electronic Medical Record" stroke={COLORS["Electronic Medical Record"]} strokeWidth={2} />
                  <Line type="monotone" dataKey="Paper/Films" stroke={COLORS["Paper/Films"]} strokeWidth={2} />
                  <Line type="monotone" dataKey="Other" stroke={COLORS["Other"]} strokeWidth={2} />
                  <Line type="monotone" dataKey="Desktop Computer" stroke={COLORS["Desktop Computer"]} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {chartType === 'percentage' && (
          <>
            <h2 className="text-xl font-semibold mb-2">Percentage Distribution of Breaches by System Location</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={percentageDistributionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line type="monotone" dataKey="Network Server (%)" stroke={COLORS["Network Server"]} strokeWidth={3} activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="Email (%)" stroke={COLORS["Email"]} strokeWidth={3} activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="Electronic Medical Record (%)" stroke={COLORS["Electronic Medical Record"]} strokeWidth={2} />
                  <Line type="monotone" dataKey="Paper/Films (%)" stroke={COLORS["Paper/Films"]} strokeWidth={2} />
                  <Line type="monotone" dataKey="Other (%)" stroke={COLORS["Other"]} strokeWidth={2} />
                  <Line type="monotone" dataKey="Desktop Computer (%)" stroke={COLORS["Desktop Computer"]} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {chartType === 'stacked' && (
          <>
            <h2 className="text-xl font-semibold mb-2">Stacked View of Breaches by System Location</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={locationTrendsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Area type="monotone" dataKey="Network Server" stackId="1" stroke={COLORS["Network Server"]} fill={COLORS["Network Server"]} />
                  <Area type="monotone" dataKey="Email" stackId="1" stroke={COLORS["Email"]} fill={COLORS["Email"]} />
                  <Area type="monotone" dataKey="Electronic Medical Record" stackId="1" stroke={COLORS["Electronic Medical Record"]} fill={COLORS["Electronic Medical Record"]} />
                  <Area type="monotone" dataKey="Paper/Films" stackId="1" stroke={COLORS["Paper/Films"]} fill={COLORS["Paper/Films"]} />
                  <Area type="monotone" dataKey="Other" stackId="1" stroke={COLORS["Other"]} fill={COLORS["Other"]} />
                  <Area type="monotone" dataKey="Desktop Computer" stackId="1" stroke={COLORS["Desktop Computer"]} fill={COLORS["Desktop Computer"]} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {chartType === 'networkServerGrowth' && (
          <>
            <h2 className="text-xl font-semibold mb-2">Annual Growth Rate of Network Server Breaches</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={networkServerGrowthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="growth" fill={COLORS["Network Server"]} name="Annual Growth Rate (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {chartType === 'growthComparison' && (
          <>
            <h2 className="text-xl font-semibold mb-2">Compound Annual Growth Rate by Location (2015-2024)</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={locationGrowthRates} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={150} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cagr" name="CAGR (%)" fill="#8884d8">
                    {locationGrowthRates.map((entry, index) => (
                      <Bar key={`bar-${index}`} dataKey="cagr" fill={entry.cagr >= 0 ? '#82ca9d' : '#ff7373'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </div>

      <div className="mt-6 w-full max-w-5xl">
        <h2 className="text-xl font-semibold mb-4">Key Insights on Breach Locations:</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li><span className="font-medium">Network Server Dominance:</span> Network server breaches have surged from just 11 cases (16.9%) in 2015 to 330 cases (63.8%) in 2024, representing a 2,900% increase and a compound annual growth rate of 45.9%.</li>
          <li><span className="font-medium">Email Security Threats:</span> Email-related breaches grew from 15 cases in 2015 to 134 in 2024 (27.6% CAGR). They peaked at 167 cases in 2020 during the COVID-19 pandemic and remote work surge.</li>
          <li><span className="font-medium">Dramatic Shift in Breach Vectors:</span> In 2015, paper/films represented the largest breach category (26.2%). By 2024, they accounted for just 2.3% of cases, showing the shift from physical to digital security threats.</li>
          <li><span className="font-medium">Electronic Medical Records:</span> EMR breaches saw a spike in 2022 (53 cases), but have generally remained a smaller proportion of overall breaches, representing only 3.3% of cases in 2024.</li>
          <li><span className="font-medium">Declining Physical Media Breaches:</span> Desktop computer and paper/films breaches have seen negative growth rates (−3.15% and −3.80% CAGR respectively), reflecting the healthcare industry's transition to cloud infrastructure.</li>
          <li><span className="font-medium">Digital Transformation Impact:</span> The data clearly shows a transition from physical security concerns (paper records, desktop computers) to network and cloud security threats, aligning with healthcare's digital transformation.</li>
        </ul>
      </div>
    </div>
  );
};

export default BreachLocationTrends;
