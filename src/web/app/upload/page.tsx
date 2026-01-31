"use client";

import { useState } from "react";
import api from "@/lib/api";
import { Upload, CheckCircle, AlertCircle, Loader2, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "success" | "error">("idle");
    const [message, setMessage] = useState("");
    const [datasetId, setDatasetId] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setStatus("idle");
            setMessage("");
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        try {
            setStatus("uploading");
            setMessage("Uploading file...");

            const formData = new FormData();
            formData.append("file", file);

            // 1. Upload
            const uploadRes = await api.post("/api/v1/datasets/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            const id = uploadRes.data.dataset_id;
            setDatasetId(id);

            // 2. Process
            setStatus("processing");
            setMessage("Processing dataset (normalizing & indexing)...");

            const processRes = await api.post(`/api/v1/datasets/${id}/process`);

            setStatus("success");
            setMessage(`Success! Loaded ${processRes.data.records} records.`);

        } catch (err: any) {
            console.error(err);
            setStatus("error");
            setMessage(err.response?.data?.detail || "An error occurred during upload.");
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Upload Dataset</h1>
                <p className="text-slate-500 mt-2">
                    Upload a raw CSV file containing student result data. The system will automatically validate and normalize it.
                </p>
            </div>

            <div className="bg-white p-8 rounded-xl border border-dashed border-slate-300 shadow-sm flex flex-col items-center justify-center text-center space-y-4">
                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center">
                    {status === "uploading" || status === "processing" ? (
                        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                    ) : (
                        <Upload className="w-8 h-8 text-blue-600" />
                    )}
                </div>

                <div className="space-y-2">
                    <label
                        htmlFor="file-upload"
                        className="cursor-pointer inline-flex items-center justify-center px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 font-medium transition-colors"
                    >
                        Choose CSV File
                    </label>
                    <input
                        id="file-upload"
                        type="file"
                        accept=".csv"
                        className="hidden"
                        onChange={handleFileChange}
                        disabled={status === "uploading" || status === "processing"}
                    />
                    <p className="text-sm text-slate-400">Supported format: .csv</p>
                </div>

                {file && (
                    <div className="flex items-center gap-2 text-slate-700 bg-slate-50 px-3 py-1 rounded-md">
                        <FileText className="w-4 h-4" />
                        <span className="text-sm font-medium">{file.name}</span>
                    </div>
                )}
            </div>

            {/* Status Message */}
            {status !== "idle" && (
                <div className={cn(
                    "p-4 rounded-lg flex items-start gap-3",
                    status === "error" ? "bg-red-50 text-red-700" :
                        status === "success" ? "bg-green-50 text-green-700" :
                            "bg-blue-50 text-blue-700"
                )}>
                    {status === "error" ? <AlertCircle className="w-5 h-5 shrink-0" /> :
                        status === "success" ? <CheckCircle className="w-5 h-5 shrink-0" /> :
                            <Loader2 className="w-5 h-5 shrink-0 animate-spin" />}

                    <div>
                        <h3 className="font-medium capitalize">{status === "processing" ? "Processing..." : status}</h3>
                        <p className="text-sm opacity-90">{message}</p>
                    </div>
                </div>
            )}

            {/* Action Button */}
            <div className="flex justify-end">
                <button
                    onClick={handleUpload}
                    disabled={!file || status === "uploading" || status === "processing" || status === "success"}
                    className={cn(
                        "px-6 py-2 rounded-lg font-medium text-white transition-all",
                        !file || status === "uploading" || status === "processing" || status === "success"
                            ? "bg-slate-300 cursor-not-allowed"
                            : "bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg"
                    )}
                >
                    {status === "processing" ? "Processing..." : "Start Upload"}
                </button>
            </div>
        </div>
    );
}
