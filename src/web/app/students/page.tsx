"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Link from "next/link";
import { Search, User, ChevronRight, Loader2 } from "lucide-react";

export default function StudentListPage() {
    const [students, setStudents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    // Debounce search could be added here
    useEffect(() => {
        async function fetchStudents() {
            try {
                setLoading(true);
                const res = await api.get(`/api/v1/students?search=${search}&limit=50`);
                setStudents(res.data.results);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }

        const timer = setTimeout(() => {
            fetchStudents();
        }, 300);

        return () => clearTimeout(timer);
    }, [search]);

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Student Profiles</h1>
                    <p className="text-slate-500">Search and view individual performance reports.</p>
                </div>

                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search by ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-64"
                    />
                </div>
            </div>

            {loading ? (
                <div className="flex py-12 justify-center">
                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {students.map((student) => (
                        <Link
                            key={student.student_id}
                            href={`/students/${student.student_id}`}
                            className="group bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all hover:border-blue-300 flex items-center justify-between"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center group-hover:bg-blue-50 transition-colors">
                                    <User className="w-6 h-6 text-slate-400 group-hover:text-blue-600" />
                                </div>
                                <div>
                                    <span className="block text-xs text-slate-400 uppercase tracking-wider font-semibold">Student ID</span>
                                    <span className="font-bold text-lg text-slate-900">{student.student_id}</span>
                                </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-blue-500" />
                        </Link>
                    ))}

                    {students.length === 0 && (
                        <div className="col-span-full py-12 text-center text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                            No students found matching "{search}".
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
