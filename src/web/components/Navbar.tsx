"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { BarChart3, Upload, GraduationCap } from "lucide-react";

export default function Navbar() {
    const pathname = usePathname();

    const links = [
        { href: "/", label: "Dashboard", icon: BarChart3 },
        { href: "/upload", label: "Upload Data", icon: Upload },
        { href: "/students", label: "Students", icon: GraduationCap },
    ];

    return (
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                        <BarChart3 className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-xl text-slate-800">AcademicEngine</span>
                </div>

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
            </div>
        </nav>
    );
}
