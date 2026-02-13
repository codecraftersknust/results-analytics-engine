"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ZAxis } from "recharts";
import { Loader2, TrendingUp, AlertCircle, Info, Network } from "lucide-react";

export default function Dashboard() {
  // --- State Management ---
  // trends: Historical performance data for the cohort.
  // correlations: Heatmap data showing relationships between subject scores.
  // subjectAnalysis: PCA analysis results for visualizing subject latent space.
  const [trends, setTrends] = useState<any[]>([]);
  const [correlations, setCorrelations] = useState<any[]>([]);
  const [subjectAnalysis, setSubjectAnalysis] = useState<any>(null);

  // insights: NLP-generated text explanations of data patterns.
  const [insights, setInsights] = useState<string[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // Parallel Fetching
        // We request independent datasets simultaneously for performance.
        const [trendsRes, corrRes, subjRes] = await Promise.all([
          api.get("/api/v1/cohort/trends"),
          api.get("/api/v1/cohort/correlations"),
          api.get("/api/v1/cohort/subjects/analysis")
        ]);

        setTrends(trendsRes.data.trends);
        setCorrelations(corrRes.data.heatmap_data);
        setInsights(corrRes.data.insights);
        setSubjectAnalysis(subjRes.data);

      } catch (err: any) {
        console.error(err);
        // Specialized error handling for missing data
        if (err.response?.status === 503) {
          setError("No dataset loaded. Please upload data first.");
        } else {
          setError("Failed to load dashboard data.");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
        <div className="bg-red-50 p-4 rounded-full">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-semibold text-slate-800">{error}</h2>
        <a href="/upload" className="text-orange-600 hover:underline">Go to Upload Page</a>
      </div>
    );
  }

  // --- Data Transformation for Recharts ---
  // The 'trends' API returns flat records: [{subject, time_label, cohort_average_score}, ...]
  // Recharts LineChart needs 'pivoted' data: [{name: time_label, SubjectA: 80, SubjectB: 75}, ...]
  const chartData: any[] = [];
  const subjects = Array.from(new Set(trends.map((t) => t.subject)));
  const timeLabels = Array.from(new Set(trends.map((t) => t.time_label)));

  // Sort time labels (heuristic: Year X Sem Y sorts naturally as strings usually, but checking numeric index is safer if available)
  // Here we rely on the string format "Year X Sem Y" sorting correctly alphabetically.
  timeLabels.sort();

  timeLabels.forEach(label => {
    const point: any = { name: label };
    subjects.forEach(subj => {
      // Find the score for this subject at this time
      const entry = trends.find(t => t.time_label === label && t.subject === subj);
      point[subj] = entry ? Number(entry.cohort_average_score.toFixed(1)) : null;
    });
    chartData.push(point);
  });

  // Colors for consistent subject visualization
  const colors = ["#ea580c", "#db2777", "#ca8a04", "#16a34a", "#9333ea", "#0891b2"];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Cohort Overview</h1>
        <p className="text-slate-500">Global performance trends across semesters.</p>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* --- Cohort Trends Chart --- */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-orange-600" />
            Performance Trends
          </h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                <YAxis domain={[0, 100]} fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend />
                {subjects.map((subj, i) => (
                  <Line
                    key={subj}
                    type="monotone"
                    dataKey={subj}
                    stroke={colors[i % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 4, strokeWidth: 0 }}
                    activeDot={{ r: 6 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* --- Insights & Correlations Panel --- */}
        <div className="space-y-6">
          {/* Key Insights Card */}
          <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-xl border border-orange-100">
            <h3 className="text-lg font-semibold text-orange-900 mb-4 flex items-center gap-2">
              <Info className="w-5 h-5" />
              Key Findings
            </h3>
            {insights.length > 0 ? (
              <ul className="space-y-3">
                {insights.map((insight, i) => (
                  <li key={i} className="text-sm text-orange-800 leading-relaxed bg-white/50 p-3 rounded-lg border border-orange-100/50">
                    {insight}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-orange-500 italic">No significant correlations detected yet.</p>
            )}
          </div>

          {/* Correlation Matrix Mini-View */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Subject Correlations</h3>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {correlations.slice(0, 8).map((point, i) => ( // Show top few interactions
                <div key={i} className="flex justify-between items-center p-2 bg-slate-50 rounded">
                  <span className="truncate w-24" title={`${point.x} vs ${point.y}`}>
                    {point.x} / {point.y}
                  </span>
                  <span className={`font-mono font-bold ${point.value > 0.5 ? 'text-green-600' : 'text-slate-500'}`}>
                    {point.value.toFixed(2)}
                  </span>
                </div>
              ))}
              {correlations.length > 8 && (
                <p className="col-span-2 text-center text-xs text-slate-400 mt-2">
                  ...and {correlations.length - 8} more
                </p>
              )}
            </div>
          </div>
        </div>
      </div>


      {/* --- Subject Relationships (PCA Visualization) --- */}
      {/* Visualizes the latent structure of the subjects. */}
      {
        subjectAnalysis && !subjectAnalysis.error && (
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Network className="w-5 h-5 text-indigo-600" />
                  Subject Relationships (Latent Space)
                </h3>
                <p className="text-sm text-slate-500 mt-1">
                  Subjects closer together are strongly correlated. Size represents student enrollment.
                  <br />
                  Color intensity represents subject difficulty (Darker = Harder).
                </p>
              </div>
              <div className="text-xs text-right text-slate-400">
                PCA Variance Explained: {subjectAnalysis.variance_explained.join(", ")}
              </div>
            </div>

            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" dataKey="x" name="Latent Factor 1" unit="" />
                  <YAxis type="number" dataKey="y" name="Latent Factor 2" unit="" />
                  <ZAxis type="number" dataKey="student_count" range={[100, 1000]} name="Students" />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-slate-200 shadow-lg rounded-lg">
                          <p className="font-bold text-slate-900">{data.subject}</p>
                          <p className="text-sm text-slate-600">Students: {data.student_count}</p>
                          <p className="text-sm text-slate-600">Avg Score: {data.avg_score}</p>
                          <p className="text-xs text-slate-400 mt-1">Latent Pos: ({data.x}, {data.y})</p>
                        </div>
                      );
                    }
                    return null;
                  }} />
                  <Scatter name="Subjects" data={subjectAnalysis.subjects} fill="#ea580c">
                    {/* Custom Label could be added here */}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        )
      }
    </div >
  );
}
