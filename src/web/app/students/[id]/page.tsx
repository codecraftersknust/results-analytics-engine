"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useParams } from "next/navigation";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { Loader2, TrendingUp, BookOpen, AlertCircle, Brain, LineChart as ChartIcon } from "lucide-react";

export default function StudentDetailPage() {
    const params = useParams();
    const id = params.id;

    // --- State Management ---
    // data: Basic student academic history and summary stats.
    // mlProfile: result from K-Means Clustering (e.g., "Consistent High Performer").
    // forecast: Linear Regression result for next semester's score.
    // risk: Heuristic risk assessment level (Low/Moderate/Critical).
    const [data, setData] = useState<any>(null);
    const [mlProfile, setMlProfile] = useState<any>(null);
    const [forecast, setForecast] = useState<any>(null);
    const [risk, setRisk] = useState<any>(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Mapping of internal risk codes to human-readable UIs
    const RISK_FACTOR_MAP: Record<string, string> = {
        "RISK_LOW_AVG": "Low Average Score",
        "RISK_TREND_STEEP_DOWN": "Strong Downward Trend",
        "RISK_TREND_DOWN": "Downward Trend",
        "RISK_HIGH_VAR": "High Performance Variance",
        "RISK_SUDDEN_DROP": "Sudden Score Drop"
    };

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                // Parallel Data Fetching
                // We fetch the basic summary and all ML insights concurrently to minimize load time.
                const [res, mlRes, forecastRes, riskRes] = await Promise.all([
                    api.get(`/api/v1/students/${id}/summary`),
                    api.get(`/api/v1/students/${id}/ml/profile`),
                    api.get(`/api/v1/students/${id}/ml/forecast`),
                    api.get(`/api/v1/students/${id}/ml/risk`)
                ]);
                setData(res.data);
                setMlProfile(mlRes.data);
                setForecast(forecastRes.data);
                setRisk(riskRes.data);
            } catch (err: any) {
                console.error(err);
                setError("Student not found or data error.");
            } finally {
                setLoading(false);
            }
        }

        if (id) fetchData();
    }, [id]);

    if (loading) return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="w-8 h-8 text-orange-600 animate-spin" /></div>;
    if (error || !data) return <div className="p-8 text-center text-red-600">{error}</div>;

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            {/* --- Header Section --- */}
            <div className="flex items-center gap-6 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <div className="w-16 h-16 bg-orange-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold">
                    {data.student_id.toString().slice(-2)}
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Student #{data.student_id}</h1>
                    <div className="flex gap-4 mt-2 text-sm text-slate-500">
                        <span className="flex items-center gap-1"><TrendingUp className="w-4 h-4" /> Avg: <span className="font-semibold text-slate-900">{data.overall_average}</span></span>
                        <span className="flex items-center gap-1"><BookOpen className="w-4 h-4" /> Semesters: <span className="font-semibold text-slate-900">{data.total_semesters}</span></span>
                    </div>
                </div>

                {/* ML Profile Badge */}
                {/* Displays the cluster label assigned to the student */}
                {mlProfile && (
                    <div className="ml-auto bg-orange-50 px-6 py-4 rounded-xl border border-orange-100 flex flex-col items-end">
                        <div className="flex items-center gap-2 text-orange-700 font-semibold mb-1">
                            <Brain className="w-5 h-5" />
                            AI Learning Profile
                        </div>
                        <div className="text-2xl font-bold text-orange-900">{mlProfile.label}</div>
                    </div>
                )}
            </div>

            {/* --- Forecast Section --- */}
            {/* Visualizes the predicted score from Linear Regression */}
            {forecast && (
                <div className="bg-gradient-to-r from-orange-500 to-amber-600 p-6 rounded-xl text-white shadow-lg">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-bold flex items-center gap-2">
                            <ChartIcon className="w-6 h-6" />
                            Performance Forecast
                        </h3>
                        <span className="bg-white/20 px-3 py-1 rounded-full text-sm font-medium">
                            Confidence: {(forecast.confidence * 100).toFixed(0)}%
                        </span>
                    </div>
                    <div className="flex items-end gap-2">
                        <span className="text-4xl font-bold">{forecast.predicted_score}</span>
                        <span className="text-orange-100 mb-1">expected for next semester</span>
                    </div>
                    <p className="mt-2 text-orange-100 text-sm opacity-80">
                        Based on linear regression of historical performance trends.
                    </p>
                </div>
            )}

            {/* --- Risk Assessment Section --- */}
            {/* Color-coded card based on risk level with explanation of factors */}
            {risk && (
                <div className={`p-6 rounded-xl border flex flex-col items-center justify-center text-center shadow-sm
                    ${risk.label === 'CRITICAL' ? 'bg-red-50 border-red-200 text-red-900' :
                        risk.label === 'MODERATE' ? 'bg-orange-50 border-orange-200 text-orange-900' :
                            'bg-green-50 border-green-200 text-green-900'}`}>

                    <div className="flex items-center gap-2 font-bold text-xl mb-2">
                        <AlertCircle className="w-6 h-6" />
                        Risk Assessment: {risk.label}
                    </div>

                    <div className="text-4xl font-bold mb-2">
                        {(risk.probability * 100).toFixed(0)}%
                    </div>
                    <div className="text-sm font-medium mb-4 opacity-80">Probability of Decline</div>

                    {/* List specific reasons why the student is at risk */}
                    {risk.factors.length > 0 && (
                        <div className="w-full text-left bg-white/50 p-4 rounded-lg">
                            <p className="text-xs font-semibold uppercase tracking-wider mb-2 opacity-70">Risk Factors</p>
                            <ul className="list-disc pl-4 space-y-1 text-sm">
                                {risk.factors.map((code: string, i: number) => (
                                    <li key={i}>{RISK_FACTOR_MAP[code] || code}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {risk.time_index && (
                        <div className="mt-4 text-xs opacity-60">
                            Based on data up to Sem {risk.time_index}
                        </div>
                    )}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* --- Performance History Chart --- */}
                <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-semibold mb-6">Performance History</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.history}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis dataKey="time_label" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                                <YAxis domain={[0, 100]} fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                <Bar dataKey="average_score" fill="#ea580c" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* --- Automated Insights --- */}
                <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <h3 className="text-lg font-semibold mb-4 text-slate-800">Automated Insights</h3>
                    {data.insights.length > 0 ? (
                        <div className="space-y-4">
                            {data.insights.map((text: string, i: number) => (
                                <div key={i} className="flex gap-3 items-start">
                                    <div className="mt-1 w-2 h-2 rounded-full bg-orange-500 shrink-0" />
                                    <p className="text-sm text-slate-600 leading-relaxed">{text}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-slate-400 italic">No specific insights detected for this student yet.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
