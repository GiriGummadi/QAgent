"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Toaster, toast } from "react-hot-toast";

export default function QATestcaseUploader() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setFiles(e.target.files);
  };

  const handleSubmit = async () => {
    if (!files || files.length === 0) {
      toast.error("Please upload at least one file.");
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("file", files[i]);
    }

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/qa_testcases", {
        method: "POST",
        body: formData,
      });

      const isJson = res.headers
        .get("content-type")
        ?.includes("application/json");

      const data = isJson ? await res.json() : null;

      if (res.ok && data?.output) {
        setOutput(data.output);
        setDownloadUrl("http://127.0.0.1:5000/output.xlsx");
        toast.success("Test cases generated!");
      } else {
        toast.error(data?.error || "Unexpected response format.");
      }
    } catch (err) {
      console.error("Error calling backend:", err);
      toast.error("Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-12 px-4 text-gray-900 dark:text-white bg-white dark:bg-black min-h-screen">
      <Toaster position="top-right" />
      <h1 className="text-2xl font-bold mb-6 text-center">QA Testcase Generator</h1>
      <Card className="dark:bg-zinc-900">
        <CardContent className="space-y-4 p-6">
          <div className="space-y-2">
            <Label htmlFor="file">Upload SRS or Screenshots</Label>
            <Input id="file" type="file" multiple onChange={handleFileChange} />
          </div>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Generating..." : "Generate Test Cases"}
          </Button>
          {downloadUrl && (
            <a href={downloadUrl} download>
              <Button variant="outline" className="mt-2">
                Download Excel
              </Button>
            </a>
          )}
        </CardContent>
      </Card>

      {output && (
        <div className="mt-8 bg-gray-100 dark:bg-zinc-800 p-4 rounded text-sm whitespace-pre-wrap max-h-[400px] overflow-auto">
          <strong className="block mb-2">Generated Test Cases:</strong>
          {output}
        </div>
      )}
    </div>
  );
}
