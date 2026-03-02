"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { BarChart3, Upload, GraduationCap, LogOut } from "lucide-react";
import { useAuth } from "@/lib/AuthContext";

export default function Navbar() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    if (!user) return null; // Hide navbar on login page

    const links = [
        { href: "/", label: "Dashboard", icon: BarChart3 },
        { href: "/students", label: "Students", icon: GraduationCap },
    ];

    if (user.role === "admin") {
        links.push({ href: "/upload", label: "Upload Data", icon: Upload });
    }

    return (
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                        <BarChart3 className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-xl text-slate-800">Graide</span>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                        {links.map((link) => {
                            const isActive = pathname === link.href;
                            const Icon = link.icon;

                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={cn(
                                        "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors",
                                        isActive
                                            ? "bg-orange-50 text-orange-700"
                                            : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                                    )}
                                >
                                    <Icon className="w-4 h-4" />
                                    {link.label}
                                </Link>
                            );
                        })}
                    </div>

                    {/* User Profile & Logout */}
                    <div className="flex items-center gap-4 ml-2 pl-4 border-l border-slate-200">
                        <div className="flex flex-col text-right">
                            <span className="text-sm font-semibold text-slate-800">{user.name}</span>
                            <span className="text-xs text-slate-500 capitalize">{user.role}</span>
                        </div>
                        <button
                            onClick={logout}
                            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                            title="Logout"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
