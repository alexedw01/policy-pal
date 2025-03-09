import { getBillDemographics } from '@/lib/api';
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Tooltip, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend} from 'recharts';

// Custom tick component to rotate labels and prevent cutoff
const CustomizedAxisTick = (props: any) => {
    const { x, y, payload, fontSize = 10 } = props;
    const label = payload.value as string;
    // Split the label on spaces to allow multi-line rendering
    const words = label.split(' ');
    return (
      <g transform={`translate(${x},${y})`}>
        <text textAnchor="end" fill="#666" fontSize={fontSize} transform="rotate(-45)">
          {words.map((word, index) => (
            <tspan key={index} x={0} dy={index === 0 ? 0 : fontSize + 2}>
              {word}
            </tspan>
          ))}
        </text>
      </g>
    );
  };

interface ChartsProps {
    billId: string;
  }

export default function Charts({ billId }: ChartsProps) {

  const [demographics, setDemographics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const categories = [
    { label: 'Political Affiliation', key: 'political_affiliation_distribution' },
    { label: 'Age Brackets', key: 'age_distribution' },
    { label: 'Gender', key: 'gender_distribution' },
    { label: 'Ethnicity', key: 'ethnicity_distribution' },
    { label: 'States', key: 'state_distribution' },
  ];

  const [selectedCategory, setSelectedCategory] = useState('political_affiliation_distribution');

  const customOrdering: Record<string, { order: string[]; rename: Record<string, string> }> = {
    political_affiliation_distribution: {
      order: ['democrat', 'republican', 'independent', 'libertarian', 'green', 'conservative', 'progressive', 'moderate', 'socialist', 'communist', 'other'],
      rename: {
        democrat: 'Democrat',
        republican: 'Republican',
        independent: 'Independent',
        libertarian: 'Libertarian',
        green: 'Green',
        conservative: 'Conservative',
        progressive: 'Progressive',
        moderate: 'Moderate',
        socialist: 'Socialist',
        communist: 'Communist',
        other: 'Other',
      },
    },
    age_distribution: {
      order: ['under_18', '18_to_30', '30_to_60', '60_plus'],
      rename: {
        'under_18': '<18',
        '18_to_30': '18-30',
        '30_to_60': '30-60',
        '60_plus': '60+',
      },
    },
    gender_distribution: {
      order: ['male', 'female', 'non-binary', 'transgender','other'],
      rename: {
        'male': 'Male',
        'female':'Female',
        'non-binary':'Non-Binary',
        'transgender':'Trans',
        'other':'Other',
      },
    },
    ethnicity_distribution: {
      order: ['hispanic or latino', 'white', 'black or african american', 'asian',
        'native hawaiian or other pacific islander', 'american indian or alaska native','other'],
      rename: {
        'hispanic or latino': 'Hispanic',
        'white': 'White',
        'black or african american': 'Black',
        'asian': 'Asian',
        'native hawaiian or other pacific islander':'Pacific Islander',
        'american indian or alaska native':'Native American',
        'other':'Other',
        },
    },
    state_distribution:{
      order:['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia',
             'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj',
             'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt',
              'va', 'wa', 'wv', 'wi', 'wy', 'other'],
      rename:{'al':'AL', 'ak':'AK', 'az':'AZ', 'ar':'AR', 'ca':'CA', 'co':'CO', 'ct':'CT', 'de':'DE', 
              'fl':'FL', 'ga':'GA', 'hi':'HI', 'id':'ID', 'il':'IL', 'in':'IN', 'ia':'IA','ks':'KS', 
              'ky':'KY', 'la':'LA', 'me':'ME', 'md':'MD', 'ma':'MA', 'mi':'MI', 'mn':'MN', 'ms':'MS',
              'mo':'MO', 'mt':'MT', 'ne':'NE', 'nv':'NV', 'nh':'NH', 'nj':'NJ','nm':'NM', 'ny':'NY',
              'nc':'NC', 'nd':'ND', 'oh':'OH', 'ok':'OK', 'or':'OR', 'pa':'PA', 'ri':'RI', 'sc':'SC',
              'sd':'SD', 'tn':'TN', 'tx':'TX', 'ut':'UT', 'vt':'VT','va':'VA', 'wa':'WA', 'wv':'WV',
              'wi':'WI', 'wy':'WY', 'other':'Other'},
    },
  };

  useEffect(() => {  // Fetch demographics when component loads
    getBillDemographics(parseInt(billId))
      .then((data) => {
        setDemographics(data.demographics);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [billId]);

  if (loading) return <p>Loading demographics...</p>;
  if (error) return <p>Error: {error}</p>;

  const distributionUp = demographics.upvote[selectedCategory] || {};
  const distributionDown = demographics.downvote[selectedCategory] || {};

  const ordering = customOrdering[selectedCategory]?.order || Object.keys(distributionUp);
  const renaming = customOrdering[selectedCategory]?.rename || {};

  const barChartData = ordering.map((key) => {
    const displayName = renaming[key] || key;
    const upCount = distributionUp[key] || 0;
    const downCount = distributionDown[key] || 0;
    const total = upCount + downCount;
    return {
      name: displayName,
      up: total > 0 ? parseFloat(((upCount / total) * 100).toFixed(1)) : 0,
      down: total > 0 ? parseFloat(((downCount / total) * 100).toFixed(1)) : 0,
    };
  });

  // Prepare data for the pie chart (total vote counts)
  const pieChartData = ordering.map((key) => {
    const displayName = renaming[key] || key;
    const upCount = distributionUp[key] || 0;
    const downCount = distributionDown[key] || 0;
    return {
      name: displayName,
      value: upCount + downCount,
    };
  });

  const pieColors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#FF6666', '#66FF66'];

  return (
    <>
      {/* Dropdown for selecting demographic category */}
      <div style={{ margin: '20px 0' }}>
        <label htmlFor="category-select">Select Demographic Category: </label>
        <select
          id="category-select"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map((cat) => (
            <option key={cat.key} value={cat.key}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      {/* Charts display */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-around',
          marginTop: '20px',
        }}
      >
        {/* Bar Chart: Percentage Breakdown */}
        <div>
          <h3>
            {categories.find((cat) => cat.key === selectedCategory)?.label} - Vote Percentages
          </h3>
          <BarChart
            width={700}
            height={350}
            data={barChartData}
            margin={{ top: 20, right: 20, bottom: 80, left: 20 }} // increased bottom margin for multi-line labels
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" 
            tick={ selectedCategory === 'state_distribution' ? <CustomizedAxisTick fontSize={11} /> : <CustomizedAxisTick fontSize={16} />}
            interval={0} />
            <YAxis domain={[0, 100]} tickFormatter={(tick) => `${tick}%`} />
            <Tooltip formatter={(value) => `${value}%`} />
            <Legend verticalAlign="bottom" align="center" wrapperStyle={{ paddingTop: 45 }} />
            <Bar dataKey="up" fill="#82ca9d" name="Upvotes (%)" />
            <Bar dataKey="down" fill="#8884d8" name="Downvotes (%)" />
          </BarChart>
        </div>

        {/* Pie Chart: Total Vote Counts */}
        <div>
          <h3>
            {categories.find((cat) => cat.key === selectedCategory)?.label} - Total Votes
          </h3>
          <PieChart width={500} height={300}>
            <Pie
              data={pieChartData}
              cx={250}
              cy={150}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              label
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>
    </>
  );
}
