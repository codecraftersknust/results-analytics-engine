"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useParams } from "next/navigation";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { Loader2, TrendingUp, BookOpen, AlertCircle } from "lucide-react";

export default function StudentDetailPage() {
    const params = useParams();
    const id = params.id;

    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const res = await api.get(`/api/v1/students/${id}/summary`);
                setData(res.data);
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
            {/* Header */}
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
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Performance Chart */}
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

                {/* NLP Insights */}
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
