import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import * as api from '../../api/api';

import {
  Upload,
  FileText,
  Trash2,
  CheckCircle2,
  Clock,
  AlertCircle,
  Database,
  Layers,
  Search,
  Plus,
  ShieldCheck,
  Cpu
} from 'lucide-react';

export const DocumentManagement: React.FC = () => {
  const { documents, addDocument, deleteDocument } = useApp();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [category, setCategory] = useState('Billing & Payments');
  const [docNameInput, setDocNameInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalName = docNameInput.trim() || (selectedFile ? selectedFile.name : 'Company_Knowledge_Doc.pdf');
    const ext = finalName.split('.').pop()?.toLowerCase() || 'pdf';
    let fileType: 'pdf' | 'docx' | 'txt' | 'markdown' = 'pdf';
    if (ext === 'docx') fileType = 'docx';
    if (ext === 'txt') fileType = 'txt';
    if (ext === 'md' || ext === 'markdown') fileType = 'markdown';

    console.log("filename: ", finalName)
    setIsUploading(true);

    const response = await api.services.uploadDoc(selectedFile)
    console.log("response: ", response)
    setTimeout(() => {
      addDocument({
        name: finalName,
        fileSize: selectedFile ? `${(selectedFile.size / 1024 / 1024).toFixed(1)} MB` : '1.8 MB',
        fileType,
        category,
        uploadedBy: 'Company Admin'
      });

      setSelectedFile(null);
      setDocNameInput('');
      setIsUploading(false);
    }, 600);
  };

  const filteredDocs = documents.filter(
    (doc) =>
      doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Top Banner / Headline */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 font-medium text-xs mb-1">
            <Database className="w-4 h-4" />
            <span>Admin Knowledge Hub</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Company Knowledge Base & Vector Indexer
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Upload official company documents (SLA guides, refund policies, product manuals). These documents are automatically chunked, embedded, and served to customer queries.
          </p>
        </div>

        <div className="flex items-center space-x-4 bg-slate-950 p-4 rounded-xl border border-slate-800 shrink-0">
          <div>
            <div className="text-xs text-slate-400">Total Knowledge Base</div>
            <div className="text-xl font-bold text-white flex items-center gap-1.5">
              <span>{documents.length} Files</span>
              <span className="text-xs text-emerald-400 font-normal">
                ({documents.filter((d) => d.status === 'indexed').length} Indexed)
              </span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Form Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Upload className="w-5 h-5 text-indigo-400" />
              Upload New Document
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Supports PDF, DOCX, TXT, and Markdown files up to 25MB
            </p>
          </div>

          <form onSubmit={handleUploadSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Document Title / Filename
              </label>
              <input
                type="text"
                value={docNameInput}
                onChange={(e) => setDocNameInput(e.target.value)}
                placeholder="e.g. Employee_Handbook_2026.pdf"
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Category Domain
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-slate-100 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition"
              >
                <option value="Billing & Payments">Billing & Payments</option>
                <option value="Engineering & API">Engineering & API</option>
                <option value="Legal & SLA">Legal & SLA</option>
                <option value="Human Resources">Human Resources</option>
                <option value="Product Operations">Product Operations</option>
              </select>
            </div>

            {/* Drag & Drop Box */}
            <div className="border-2 border-dashed border-slate-700/80 hover:border-indigo-500/80 bg-slate-950/60 rounded-2xl p-6 text-center transition cursor-pointer">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf,.docx,.txt,.md"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSelectedFile(e.target.files[0]);
                  }
                }}
              />
              <label htmlFor="file-upload" className="cursor-pointer space-y-2">
                <div className="w-12 h-12 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto">
                  <Upload className="w-6 h-6" />
                </div>
                <div className="text-xs font-semibold text-slate-200">
                  {selectedFile ? selectedFile.name : 'Click to select document or drag & drop'}
                </div>
                <div className="text-[11px] text-slate-500">PDF, DOCX, Markdown, or TXT</div>
              </label>
            </div>

            <button
              type="submit"
              disabled={isUploading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/20"
            >
              {isUploading ? (
                <span>Ingesting Document...</span>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Index Document to Vector Store</span>
                </>
              )}
            </button>
          </form>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 space-y-2 text-xs text-slate-400">
            <div className="flex items-center text-indigo-400 font-semibold gap-1.5">
              <ShieldCheck className="w-4 h-4" />
              <span>RAG Pipeline Architecture</span>
            </div>
            <p className="text-[11px] leading-relaxed">
              Files are split into 512-token chunks with 50-token overlap, embedded using OpenAI/BGE embeddings, and saved in ChromaDB vector storage.
            </p>
          </div>
        </div>

        {/* Documents Table / List */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Uploaded Company Documents</h2>
              <p className="text-xs text-slate-400">
                Manage files active in the bot's knowledge base
              </p>
            </div>

            {/* Search Bar */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-slate-100 rounded-xl pl-9 pr-4 py-2 text-xs focus:outline-none focus:border-indigo-500 transition w-full sm:w-64"
              />
            </div>
          </div>

          {/* Table Container */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Document</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Chunks</th>
                  <th className="px-4 py-3">Uploaded</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3.5">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-100">{doc.name}</div>
                          <div className="text-[10px] text-slate-400">
                            {doc.fileSize} • {doc.fileType.toUpperCase()}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="px-4 py-3.5">
                      <span className="bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md text-[11px] font-medium border border-slate-700/60">
                        {doc.category}
                      </span>
                    </td>

                    <td className="px-4 py-3.5">
                      {doc.status === 'indexed' && (
                        <span className="inline-flex items-center space-x-1 bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-medium text-[11px]">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Indexed</span>
                        </span>
                      )}
                      {doc.status === 'processing' && (
                        <span className="inline-flex items-center space-x-1 bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded border border-amber-500/20 font-medium text-[11px] animate-pulse">
                          <Clock className="w-3 h-3" />
                          <span>Vectorizing</span>
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="inline-flex items-center space-x-1 bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded border border-rose-500/20 font-medium text-[11px]">
                          <AlertCircle className="w-3 h-3" />
                          <span>Failed</span>
                        </span>
                      )}
                    </td>

                    <td className="px-4 py-3.5 font-medium text-slate-300">
                      <div className="flex items-center space-x-1">
                        <Layers className="w-3.5 h-3.5 text-slate-400" />
                        <span>{doc.chunksCount} chunks</span>
                      </div>
                    </td>

                    <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                      {doc.uploadDate}
                    </td>

                    <td className="px-4 py-3.5 text-right">
                      <button
                        onClick={() => deleteDocument(doc.id)}
                        className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition"
                        title="Delete Document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
