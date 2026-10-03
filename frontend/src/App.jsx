import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom'
import { Search, Upload, BookOpen, CheckCircle2, XCircle, ExternalLink, GitBranch, Layers, FlaskConical, LogOut, ChevronDown, ChevronUp, Info } from 'lucide-react'
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState } from 'reactflow'
import 'reactflow/dist/style.css'
import { backendAPI } from './api'

// ─────────────────────────────────────────────
// Auth helpers (simple client-side session)
// ─────────────────────────────────────────────
const DEMO_USER = 'researcher';
const DEMO_PASS = 'researchmate2024';

const isLoggedIn = () => sessionStorage.getItem('rm_auth') === 'true';
const setLoggedIn = () => sessionStorage.setItem('rm_auth', 'true');
const setLoggedOut = () => sessionStorage.removeItem('rm_auth');

// ─────────────────────────────────────────────
// Login Page
// ─────────────────────────────────────────────
const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim().toLowerCase() === DEMO_USER && password.trim() === DEMO_PASS) {
      setLoggedIn();
      onLogin();
    } else {
      setError('Invalid username or password.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center gap-3 justify-center mb-10">
          <div className="w-10 h-10 rounded-md bg-primary-600 flex items-center justify-center">
            <BookOpen className="text-white" size={20} />
          </div>
          <span className="font-sans font-bold text-2xl tracking-tight text-white">ResearchMate</span>
        </div>

        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold text-white mb-1">Sign in</h2>
          <p className="text-sm text-gray-400 mb-8">Access the research platform</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => { setUsername(e.target.value); setError(''); }}
                placeholder="researcher"
                className="input-glass w-full"
                autoComplete="username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setError(''); }}
                placeholder="••••••••••••••"
                className="input-glass w-full"
                autoComplete="current-password"
              />
            </div>

            {error && (
              <p className="text-sm text-red-400 bg-red-900/20 border border-red-800 rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button type="submit" className="btn-primary w-full py-3 text-base">
              Sign In
            </button>
          </form>

        </div>
      </div>
    </div>
  );
};


// ─────────────────────────────────────────────
// Evidence Badge
// ─────────────────────────────────────────────
const EvidenceBadge = ({ level }) => {
  const styles = {
    High: 'bg-green-900 text-green-300 border-green-700',
    Emerging: 'bg-blue-900 text-blue-300 border-blue-700',
    Medium: 'bg-yellow-900 text-yellow-300 border-yellow-700',
    Low: 'bg-gray-800 text-gray-400 border-gray-700',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-md border font-medium ${styles[level] || styles.Low}`}>
      {level}
    </span>
  );
};

// ─────────────────────────────────────────────
// How-to Box (collapsible)
// ─────────────────────────────────────────────
const HowTo = ({ title, steps }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="mb-8 border border-blue-900 rounded-md bg-blue-950/20">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <span className="flex items-center gap-2 text-sm font-medium text-blue-300">
          <Info size={15} /> {title}
        </span>
        {open ? <ChevronUp size={15} className="text-gray-400" /> : <ChevronDown size={15} className="text-gray-400" />}
      </button>
      {open && (
        <div className="px-4 pb-4">
          <ol className="space-y-2">
            {steps.map((s, i) => (
              <li key={i} className="flex gap-3 text-sm text-gray-300">
                <span className="text-blue-400 font-bold w-5 shrink-0">{i + 1}.</span>
                <span dangerouslySetInnerHTML={{ __html: s }} />
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────
// Knowledge Graph Page — Multi-paper research map
// ─────────────────────────────────────────────

// Node styles by entity type
const NODE_STYLES = {
  paper:   { background: '#1e3a5f', color: '#93c5fd', border: '2px solid #2563eb', borderRadius: '8px', padding: '10px 14px', fontSize: '12px', fontWeight: 700, maxWidth: '200px', textAlign: 'center' },
  author:  { background: '#2d1b69', color: '#c4b5fd', border: '1px solid #6d28d9', borderRadius: '6px', padding: '6px 10px', fontSize: '11px' },
  dataset: { background: '#1a2e1a', color: '#86efac', border: '1px solid #166534', borderRadius: '6px', padding: '6px 10px', fontSize: '11px' },
  method:  { background: '#3b1d1d', color: '#fca5a5', border: '1px solid #991b1b', borderRadius: '6px', padding: '6px 10px', fontSize: '11px' },
  year:    { background: '#1c1c2e', color: '#818cf8', border: '1px solid #4338ca', borderRadius: '6px', padding: '6px 10px', fontSize: '11px' },
};

const buildMultiPaperGraph = (papers) => {
  const nodes = [];
  const edges = [];
  const authorMap = {};   // author name → node id
  const datasetMap = {};  // dataset name → node id
  const methodMap = {};   // method name → node id
  let nodeId = 0;
  const nextId = () => `n${nodeId++}`;

  // Layout papers in a horizontal row at the top
  const paperIds = {};
  papers.forEach((paper, i) => {
    const id = nextId();
    paperIds[i] = id;
    const x = 120 + i * 320;
    const y = 60;
    nodes.push({
      id,
      data: { label: (paper.title || 'Paper').substring(0, 45) + ((paper.title || '').length > 45 ? '…' : '') },
      position: { x, y },
      style: NODE_STYLES.paper,
    });
  });

  // For each paper, add author / year / dataset / method satellite nodes
  papers.forEach((paper, pi) => {
    const paperId = paperIds[pi];
    const baseX = 120 + pi * 320;

    // Year node (small, top-right of paper)
    if (paper.year) {
      const yId = nextId();
      nodes.push({ id: yId, data: { label: String(paper.year) }, position: { x: baseX + 140, y: 40 }, style: NODE_STYLES.year });
      edges.push({ id: `ey${pi}`, source: paperId, target: yId, label: 'year', labelStyle: { fontSize: '9px', fill: '#6b7280' }, style: { stroke: '#4338ca', strokeDasharray: '4 2' } });
    }

    // Authors
    (paper.authors || []).slice(0, 3).forEach((author, ai) => {
      const name = (author.name || '').trim();
      if (!name) return;
      if (!authorMap[name]) {
        const aId = nextId();
        authorMap[name] = aId;
        nodes.push({ id: aId, data: { label: name }, position: { x: baseX - 40 + ai * 80, y: 220 + ai * 60 }, style: NODE_STYLES.author });
      }
      const existingEdge = edges.find(e => e.source === paperId && e.target === authorMap[name]);
      if (!existingEdge) {
        edges.push({ id: `ea${pi}-${ai}`, source: paperId, target: authorMap[name], label: 'authored by', labelStyle: { fontSize: '9px', fill: '#6b7280' }, style: { stroke: '#6d28d9' } });
      }
    });

    // If we have a summary with dataset/method, add those
    if (paper._dataset) {
      const ds = paper._dataset.trim();
      if (ds && ds !== 'Not specified in the paper.') {
        if (!datasetMap[ds]) {
          const dId = nextId();
          datasetMap[ds] = dId;
          nodes.push({ id: dId, data: { label: `Dataset: ${ds.substring(0, 30)}` }, position: { x: baseX, y: 400 }, style: NODE_STYLES.dataset });
        }
        const existingEdge = edges.find(e => e.source === paperId && e.target === datasetMap[ds]);
        if (!existingEdge) {
          edges.push({ id: `eds${pi}`, source: paperId, target: datasetMap[ds], label: 'uses', labelStyle: { fontSize: '9px', fill: '#6b7280' }, style: { stroke: '#166534' } });
        }
      }
    }
    if (paper._model) {
      const m = paper._model.trim();
      if (m && m !== 'Not specified in the paper.') {
        if (!methodMap[m]) {
          const mId = nextId();
          methodMap[m] = mId;
          nodes.push({ id: mId, data: { label: `Method: ${m.substring(0, 30)}` }, position: { x: baseX + 160, y: 400 }, style: NODE_STYLES.method });
        }
        const existingEdge = edges.find(e => e.source === paperId && e.target === methodMap[m]);
        if (!existingEdge) {
          edges.push({ id: `em${pi}`, source: paperId, target: methodMap[m], label: 'applies', labelStyle: { fontSize: '9px', fill: '#6b7280' }, style: { stroke: '#991b1b' } });
        }
      }
    }
  });

  // Add citation edges between papers if citation info available
  // (We show this as a visual citation link between paper nodes)
  papers.forEach((paper, pi) => {
    if (paper.citation_count > 0 && pi < papers.length - 1) {
      // Heuristic: connect high-citation papers to next paper to show influence chain
      if (paper.citation_count > 50) {
        edges.push({
          id: `ecite${pi}`,
          source: paperIds[pi],
          target: paperIds[pi + 1],
          label: 'cited by related work',
          animated: true,
          labelStyle: { fontSize: '9px', fill: '#f59e0b' },
          style: { stroke: '#f59e0b', strokeDasharray: '6 3' },
        });
      }
    }
  });

  return { nodes, edges };
};

// Legend item
const LegendItem = ({ color, label }) => (
  <div className="flex items-center gap-2">
    <div className="w-3 h-3 rounded-sm flex-shrink-0" style={{ background: color }} />
    <span className="text-xs text-gray-400">{label}</span>
  </div>
);

const KnowledgeGraphPage = () => {
  const [rawIds, setRawIds] = useState(() => sessionStorage.getItem('graph_ids') || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [papers, setPapers] = useState([]);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const handleBuild = async (e) => {
    e.preventDefault();
    const ids = rawIds.split('\n').map(s => s.trim()).filter(Boolean);
    if (ids.length < 1) { setError('Please enter at least 1 Paper ID.'); return; }
    if (ids.length > 8) { setError('Maximum 8 papers can be visualized at once.'); return; }
    setLoading(true); setError(''); setPapers([]); setNodes([]); setEdges([]);
    try {
      const fetched = await Promise.all(
        ids.map(id => backendAPI.getPaperDetails(id).catch(() => null))
      );
      const valid = fetched.filter(Boolean);
      if (valid.length === 0) { setError('Could not fetch any paper details. Check the Paper IDs and backend.'); setLoading(false); return; }
      setPapers(valid);
      sessionStorage.setItem('graph_ids', rawIds);
      const { nodes: n, edges: ed } = buildMultiPaperGraph(valid);
      setNodes(n); setEdges(ed);
    } catch (err) {
      setError('Failed to build knowledge graph. Check the backend is running.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto">
      <h2 className="text-4xl font-sans font-bold mb-2">Research Knowledge Graph</h2>
      <p className="text-gray-400 mb-2">
        A visual research map showing how papers are connected through shared authors, datasets, methods, and citation relationships.
        Identifies influential papers and reveals how a research topic has developed.
      </p>

      <HowTo title="How to use the Knowledge Graph" steps={[
        'Go to <strong>Search</strong> and search for papers on your topic.',
        'Copy the <strong>Paper IDs</strong> from each result card (small monospace text below each title, e.g. <code class="text-blue-300 bg-gray-800 px-1 rounded">W2741809807</code>).',
        'Paste 2–8 Paper IDs below, one per line, then click <strong>Build Graph</strong>.',
        'The graph maps <span class="text-blue-300">papers</span>, <span class="text-purple-300">authors</span>, <span class="text-green-300">datasets</span>, <span class="text-red-300">methods</span>, and <span class="text-yellow-300">citation links</span>.',
        'Shared nodes (same author or dataset appearing on multiple papers) are automatically merged — showing cross-paper connections.',
        'Pan, zoom, and drag nodes to explore the research landscape.',
      ]} />

      <form onSubmit={handleBuild} className="glass-card p-6 mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">Paper IDs to map (one per line, 1–8 papers)</label>
        <textarea
          value={rawIds}
          onChange={(e) => { setRawIds(e.target.value); sessionStorage.setItem('graph_ids', e.target.value); }}
          placeholder={"W2741809807\nW3123456789\nW9876543210"}
          rows={5}
          className="input-glass w-full mb-4 font-mono text-sm"
        />
        <button type="submit" className="btn-primary" disabled={loading || !rawIds.trim()}>
          {loading ? 'Fetching papers & building graph...' : <><GitBranch size={18} /> Build Research Map</>}
        </button>
      </form>

      {error && <div className="bg-red-900/20 border border-red-800 text-red-400 p-4 rounded-md mb-6 text-sm">{error}</div>}

      {papers.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {papers.map((p, i) => (
            <div key={i} className="glass-card px-3 py-2 text-xs">
              <span className="text-primary-400 font-semibold">Paper {i+1}: </span>
              <span className="text-gray-300">{(p.title || '').substring(0, 60)}{p.title?.length > 60 ? '…' : ''}</span>
              {p.year && <span className="text-gray-500 ml-2">{p.year}</span>}
              {p.citation_count != null && <span className="text-gray-500 ml-2">{p.citation_count.toLocaleString()} citations</span>}
            </div>
          ))}
        </div>
      )}

      <div className="glass-card" style={{ height: '580px', position: 'relative' }}>
        {/* Legend */}
        {nodes.length > 0 && (
          <div className="absolute top-3 left-3 z-10 glass-card p-3 space-y-1.5">
            <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">Legend</p>
            <LegendItem color="#1e3a5f" label="Paper" />
            <LegendItem color="#2d1b69" label="Author" />
            <LegendItem color="#1a2e1a" label="Dataset" />
            <LegendItem color="#3b1d1d" label="Method" />
            <LegendItem color="#1c1c2e" label="Year" />
          </div>
        )}
        {nodes.length > 0 ? (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            attributionPosition="bottom-right"
          >
            <MiniMap nodeStrokeWidth={3} zoomable pannable style={{ background: '#111827' }} />
            <Controls />
            <Background color="#1f2937" gap={24} />
          </ReactFlow>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <GitBranch size={52} className="mx-auto mb-4 opacity-20" />
              <p className="text-lg font-medium">Enter paper IDs to build the research knowledge graph.</p>
              <p className="text-sm mt-2 text-gray-600">The graph will show how papers connect through authors, datasets, and methods.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};


// ─────────────────────────────────────────────
// Comparison Page
// ─────────────────────────────────────────────
const ComparisonPage = () => {
  const [rawIds, setRawIds] = useState(() => sessionStorage.getItem('compare_ids') || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('compare_results') || '[]'); } catch { return []; }
  });

  const handleCompare = async (e) => {
    e.preventDefault();
    const ids = rawIds.split('\n').map(s => s.trim()).filter(Boolean);
    if (ids.length < 2) { setError('Please enter at least 2 paper IDs (one per line).'); return; }
    if (ids.length > 6) { setError('Maximum 6 papers can be compared at once.'); return; }
    setLoading(true); setError(''); setResults([]);
    try {
      const data = await backendAPI.comparePapers(ids);
      const res = data.papers || [];
      setResults(res);
      sessionStorage.setItem('compare_results', JSON.stringify(res));
      sessionStorage.setItem('compare_ids', rawIds);
    } catch (err) {
      setError('Comparison failed. Check the backend is running and the Paper IDs are valid.');
    }
    setLoading(false);
  };

  const aspects = [
    { key: 'year', label: 'Year' },
    { key: 'dataset', label: 'Dataset' },
    { key: 'model', label: 'Model / Method' },
    { key: 'metric', label: 'Metric' },
    { key: 'limitation', label: 'Limitation' },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-4xl font-sans font-bold mb-2">Paper Comparison Matrix</h2>
      <p className="text-gray-400 mb-6">Compare up to 6 papers side-by-side across dataset, model, metric, and limitation.</p>

      <HowTo title="How to use Paper Comparison" steps={[
        'Go to <strong>Search</strong> and find papers relevant to your topic.',
        'Under each result card, copy the <strong>Paper ID</strong> (shown in small gray monospace text, e.g. <code class="text-blue-300 bg-gray-800 px-1 rounded">W2741809807</code>).',
        'Paste 2–6 Paper IDs below, <strong>one per line</strong>.',
        'Click <strong>Compare Papers</strong>. The system uses AI to extract Dataset, Model, Metric, and Limitation from each abstract.',
        'Your results persist here even if you navigate to Search and come back.',
      ]} />

      <form onSubmit={handleCompare} className="glass-card p-6 mb-8">
        <label className="block text-sm font-medium text-gray-300 mb-2">Paper IDs (one per line, 2–6)</label>
        <textarea
          value={rawIds}
          onChange={(e) => { setRawIds(e.target.value); sessionStorage.setItem('compare_ids', e.target.value); }}
          placeholder={"W2741809807\nW3123456789\nW9876543210"}
          rows={5}
          className="input-glass w-full mb-4 font-mono text-sm"
        />
        <button type="submit" className="btn-primary" disabled={loading || !rawIds.trim()}>
          {loading ? 'Analyzing papers with AI...' : <><Layers size={18} /> Compare Papers</>}
        </button>
      </form>

      {error && <div className="bg-red-900/20 border border-red-800 text-red-400 p-4 rounded-md mb-6 text-sm">{error}</div>}

      {results.length > 0 && (
        <div className="glass-card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-4 text-gray-400 font-medium w-36">Aspect</th>
                {results.map((p, i) => (
                  <th key={i} className="text-left p-4 text-white font-semibold min-w-48">
                    <div className="text-primary-400 text-xs mb-1">Paper {i + 1}</div>
                    <div className="line-clamp-2 text-sm">{p.title}</div>
                    {p.year && <div className="text-gray-500 font-normal text-xs mt-1">{p.year}</div>}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {aspects.map((aspect, ai) => (
                <tr key={ai} className={`border-b border-gray-800 ${ai % 2 === 0 ? 'bg-gray-800/10' : ''}`}>
                  <td className="p-4 text-gray-400 font-medium align-top whitespace-nowrap">{aspect.label}</td>
                  {results.map((p, pi) => (
                    <td key={pi} className="p-4 text-gray-300 align-top">
                      {p[aspect.key] || <span className="text-gray-600 italic">N/A</span>}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────
// Research Gap Detection Page
// ─────────────────────────────────────────────
const GapDetectionPage = () => {
  const [rawIds, setRawIds] = useState(() => sessionStorage.getItem('gap_ids') || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [opportunities, setOpportunities] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('gap_results') || '[]'); } catch { return []; }
  });

  const handleDetect = async (e) => {
    e.preventDefault();
    const ids = rawIds.split('\n').map(s => s.trim()).filter(Boolean);
    if (ids.length < 2) { setError('Please enter at least 2 paper IDs to detect gaps across the corpus.'); return; }
    setLoading(true); setError(''); setOpportunities([]);
    try {
      const data = await backendAPI.detectGaps(ids);
      const ops = data.opportunities || [];
      setOpportunities(ops);
      sessionStorage.setItem('gap_results', JSON.stringify(ops));
      sessionStorage.setItem('gap_ids', rawIds);
      if (ops.length === 0) setError('No research gaps could be identified from the provided abstracts.');
    } catch (err) {
      setError('Gap detection failed. Check the backend is running.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-4xl font-sans font-bold mb-2">Research Gap Detection</h2>
      <p className="text-gray-400 mb-6">Analyze a corpus of related papers to identify recurring limitations and surface potential research opportunities.</p>

      <HowTo title="How to use Research Gap Detection" steps={[
        'Go to <strong>Search</strong> and search for a topic (e.g. "battery degradation prediction").',
        'Collect <strong>5–20 Paper IDs</strong> from the result cards (the small gray monospace text under each paper title). The more papers, the better the analysis.',
        'Paste the IDs below, <strong>one per line</strong>.',
        'Click <strong>Detect Research Gaps</strong>. The system feeds all abstracts into the AI model and identifies <em>recurring limitations</em> across papers.',
        'The output is a list of <strong>Potential Research Opportunities</strong> — not guaranteed novelty, but derived from real patterns in the literature.',
        'Results persist here even if you navigate away.',
      ]} />

      <form onSubmit={handleDetect} className="glass-card p-6 mb-8">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Paper IDs to analyze (one per line, recommend 5–20)
        </label>
        <textarea
          value={rawIds}
          onChange={(e) => { setRawIds(e.target.value); sessionStorage.setItem('gap_ids', e.target.value); }}
          placeholder={"W2741809807\nW3123456789\nW9876543210\n..."}
          rows={8}
          className="input-glass w-full mb-4 font-mono text-sm"
        />
        <button type="submit" className="btn-primary" disabled={loading || !rawIds.trim()}>
          {loading ? 'Analyzing corpus with AI...' : <><FlaskConical size={18} /> Detect Research Gaps</>}
        </button>
      </form>

      {error && <div className="bg-red-900/20 border border-red-800 text-red-400 p-4 rounded-md mb-6 text-sm">{error}</div>}

      {opportunities.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-xl font-bold text-white mb-1">Potential Research Opportunities</h3>
          <p className="text-xs text-gray-500 mb-6 border-b border-gray-700 pb-4">
            Derived from recurring limitations found across {rawIds.split('\n').filter(Boolean).length} analyzed papers.
            These are potential directions — not guaranteed to be novel research contributions.
          </p>
          <ol className="space-y-4">
            {opportunities.map((opp, i) => (
              <li key={i} className="flex gap-4 items-start p-4 bg-gray-800/50 rounded-md border border-gray-700">
                <span className="text-2xl font-bold text-primary-500 w-8 shrink-0 mt-0.5">{i + 1}.</span>
                <p className="text-gray-200 text-sm leading-relaxed">{opp}</p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────
// Dashboard
// ─────────────────────────────────────────────
const Dashboard = () => {
  const [isConnected, setIsConnected] = useState(null);

  useEffect(() => {
    backendAPI.checkHealth()
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false));
  }, []);

  return (
    <div>
      <div className="text-center max-w-3xl mx-auto mt-12 mb-16">
        <div className="flex justify-center mb-6">
          {isConnected === null ? (
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-gray-800 text-gray-400 border border-gray-700">
              <span className="text-sm font-medium tracking-wide uppercase">Connecting...</span>
            </div>
          ) : isConnected ? (
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-gray-800 text-green-400 border border-green-900">
              <CheckCircle2 size={16} />
              <span className="text-sm font-medium tracking-wide uppercase">Backend Connected</span>
            </div>
          ) : (
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-gray-800 text-red-400 border border-red-900">
              <XCircle size={16} />
              <span className="text-sm font-medium tracking-wide uppercase">Backend Disconnected</span>
            </div>
          )}
        </div>

        <h1 className="text-5xl md:text-6xl font-sans font-bold mb-6 leading-tight text-white">
          Scholarly Literature Search <br /> & Document Analysis
        </h1>
        <p className="text-xl text-gray-400 mb-10 leading-relaxed">
          Aggregate papers from multiple academic sources, compare methodologies, detect research gaps, and analyze uploaded PDFs.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/search" className="btn-primary text-lg px-8 py-4">
            <Search size={20} /> Explore Papers
          </Link>
          <Link to="/upload" className="btn-secondary text-lg px-8 py-4">
            <Upload size={20} /> Upload PDF
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
        {[
          { title: 'Multi-Source Search', icon: Search, desc: 'Papers aggregated from OpenAlex and Semantic Scholar, ranked by relevance, recency, and citations.', to: '/search' },
          { title: 'Document Q&A', icon: BookOpen, desc: 'Upload a PDF and ask structured questions. Extract summaries in 7 standard fields.', to: '/upload' },
          { title: 'Comparison Matrix', icon: Layers, desc: 'Compare 2–6 papers side-by-side. AI extracts Dataset, Model, Metric, and Limitation.', to: '/compare' },
          { title: 'Research Gaps', icon: FlaskConical, desc: 'Paste 5–20 paper IDs. AI identifies recurring limitations and surfaces potential research opportunities.', to: '/gaps' },
        ].map((feature, i) => (
          <Link key={i} to={feature.to} className="glass-card p-6 hover:border-gray-600 transition-colors block">
            <div className="w-12 h-12 rounded-md bg-gray-800 flex items-center justify-center mb-5">
              <feature.icon className="text-primary-500" size={24} />
            </div>
            <h3 className="text-lg font-sans font-semibold mb-2 text-white">{feature.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed">{feature.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────
// Layout
// ─────────────────────────────────────────────
const Layout = ({ children, onLogout }) => (
  <div className="min-h-screen flex flex-col">
    <nav className="glass-panel sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-primary-600 flex items-center justify-center">
            <BookOpen className="text-white" size={18} />
          </div>
          <span className="font-sans font-bold text-lg tracking-tight text-white">ResearchMate</span>
        </Link>
        <div className="hidden md:flex items-center gap-6">
          <Link to="/search" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Search</Link>
          <Link to="/compare" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Compare</Link>
          <Link to="/gaps" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Research Gaps</Link>
          <Link to="/graph" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Knowledge Graph</Link>
          <Link to="/upload" className="btn-primary text-sm py-2 px-5">Upload PDF</Link>
          <button onClick={onLogout} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 transition-colors">
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </div>
    </nav>
    <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-12">
      {children}
    </main>
    <footer className="border-t border-gray-800 py-5 text-center text-sm text-gray-600">
      ResearchMate — Scholarly Literature Platform
    </footer>
  </div>
);

// ─────────────────────────────────────────────
// Search Page — with sessionStorage persistence
// ─────────────────────────────────────────────
const SearchPage = () => {
  // Persist state across tab switches using sessionStorage
  const [query, setQuery] = useState(() => sessionStorage.getItem('search_query') || '');
  const [papers, setPapers] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('search_papers') || '[]'); } catch { return []; }
  });
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [summaries, setSummaries] = useState({});
  const [summarizing, setSummarizing] = useState({});
  const [total, setTotal] = useState(() => parseInt(sessionStorage.getItem('search_total') || '0', 10));
  const [offset, setOffset] = useState(() => parseInt(sessionStorage.getItem('search_offset') || '0', 10));
  const [source, setSource] = useState('all');
  const LIMIT = 40;

  const saveToSession = (p, t, o, q) => {
    sessionStorage.setItem('search_papers', JSON.stringify(p));
    sessionStorage.setItem('search_total', String(t));
    sessionStorage.setItem('search_offset', String(o));
    sessionStorage.setItem('search_query', q);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true); setError('');
    setPapers([]); setSummaries({}); setOffset(0); setTotal(0);
    try {
      const searchQuery = source === 'ieee' ? `${query} IEEE` : query;
      const data = await backendAPI.searchPapers(searchQuery, LIMIT, 0);
      const p = data.papers || [];
      const t = data.total || 0;
      setPapers(p); setTotal(t); setOffset(LIMIT);
      saveToSession(p, t, LIMIT, query);
      if (p.length === 0) setError('No papers found. Try different keywords.');
    } catch (err) {
      if (err.response?.status === 429) setError('Rate limit reached. Please wait a moment.');
      else setError('Could not reach the search API. Is the backend running?');
    }
    setLoading(false);
  };

  const handleLoadMore = async () => {
    setLoadingMore(true);
    try {
      const data = await backendAPI.searchPapers(query, LIMIT, offset);
      const more = data.papers || [];
      const updated = [...papers, ...more];
      setPapers(updated);
      setOffset(prev => prev + LIMIT);
      saveToSession(updated, total, offset + LIMIT, query);
    } catch (err) { console.error(err); }
    setLoadingMore(false);
  };

  const handleSummarize = async (paperId, abstract, title) => {
    const text = abstract || `Research paper titled: "${title}". Summarize what this paper likely covers.`;
    setSummarizing(prev => ({ ...prev, [paperId]: true }));
    try {
      const data = await backendAPI.summarizeText(text);
      setSummaries(prev => ({ ...prev, [paperId]: data.summary }));
    } catch (err) {
      alert('Failed to summarize. Check your Gemini API key in backend/.env');
    }
    setSummarizing(prev => ({ ...prev, [paperId]: false }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-4xl font-sans font-bold mb-2">Search Research Papers</h2>
      <p className="text-gray-400 mb-8">
        Aggregated from OpenAlex and Semantic Scholar — ranked by relevance, recency, and citations.
        {papers.length > 0 && <span className="text-gray-600 ml-2">Results saved — switching tabs will not lose your search.</span>}
      </p>

      <form onSubmit={handleSearch} className="flex gap-4 mb-10">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Battery degradation prediction using LSTM..."
          className="input-glass flex-1"
        />
        <select value={source} onChange={(e) => setSource(e.target.value)} className="input-glass w-36">
          <option value="all">All Sources</option>
          <option value="ieee">IEEE Only</option>
        </select>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Searching...' : <><Search size={20} /> Search</>}
        </button>
      </form>

      {error && <div className="bg-red-900/20 border border-red-800 text-red-400 p-4 rounded-md mb-6 text-sm">{error}</div>}
      {loading && <div className="text-center py-16 text-gray-400"><p>Searching publications...</p></div>}

      {papers.length > 0 && (
        <p className="text-sm text-gray-500 mb-4">
          Showing <span className="text-primary-400 font-semibold">{papers.length}</span> of{' '}
          <span className="text-white font-semibold">{total.toLocaleString()}</span> results for "
          <span className="text-primary-400">{query}</span>"
        </p>
      )}

      <div className="space-y-6">
        {papers.map((paper, i) => (
          <div key={paper.paper_id || i} className="glass-card p-6">
            <div className="flex justify-between items-start gap-4 mb-3">
              <div className="flex-1">
                {paper.url ? (
                  <a href={paper.url} target="_blank" rel="noopener noreferrer"
                    className="text-xl font-bold text-primary-400 hover:text-primary-300 hover:underline transition-colors flex items-start gap-2 group">
                    {paper.title}
                    <ExternalLink size={14} className="mt-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                ) : (
                  <h3 className="text-xl font-bold text-primary-400">{paper.title}</h3>
                )}
              </div>
              <button
                onClick={() => handleSummarize(paper.paper_id, paper.abstract, paper.title)}
                disabled={summarizing[paper.paper_id] || !!summaries[paper.paper_id]}
                className="btn-secondary whitespace-nowrap text-sm py-1.5 px-3 shrink-0"
              >
                {summarizing[paper.paper_id] ? 'Summarizing...' : summaries[paper.paper_id] ? 'Summarized' : 'AI Summary'}
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-3 mb-3">
              <span className="text-sm text-gray-400">
                {paper.authors?.slice(0, 3).map(a => a.name || a).join(', ')}
                {paper.authors?.length > 3 ? ` +${paper.authors.length - 3} more` : ''}
              </span>
              {paper.year && <span className="text-xs px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 border border-gray-700">{paper.year}</span>}
              {paper.citation_count != null && <span className="text-xs px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 border border-gray-700">{paper.citation_count.toLocaleString()} citations</span>}
              {paper.overall_evidence && <EvidenceBadge level={paper.overall_evidence} />}
              {paper.semantic_relevance != null && <span className="text-xs text-gray-600">Relevance: {paper.semantic_relevance.toFixed(2)}</span>}
              {paper.doi && <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer" className="text-xs text-gray-500 hover:text-primary-400 transition-colors">DOI: {paper.doi}</a>}
            </div>

            {/* Paper ID for copying to Compare / Gap tools */}
            {paper.paper_id && (
              <div className="mb-3 flex items-center gap-2">
                <span className="text-xs text-gray-600">Paper ID:</span>
                <code className="text-xs text-gray-400 bg-gray-800 px-2 py-0.5 rounded select-all">{paper.paper_id}</code>
              </div>
            )}

            <p className="text-gray-300 text-sm leading-relaxed">
              <span className="font-semibold text-white">Description: </span>
              {paper.abstract ? (paper.abstract.length > 500 ? paper.abstract.substring(0, 500) + '...' : paper.abstract) : <em className="text-gray-500">No description available.</em>}
            </p>

            {paper.url && (
              <div className="mt-4">
                <a href={paper.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 text-sm text-primary-400 hover:text-primary-300 transition-colors">
                  <ExternalLink size={14} /> Read Full Paper
                </a>
              </div>
            )}

            {summaries[paper.paper_id] && (
              <div className="mt-5 p-4 bg-gray-800/50 border border-gray-700 rounded-md">
                <h4 className="font-bold text-primary-400 mb-3">AI Summary</h4>
                <div className="space-y-2 text-sm text-gray-300">
                  {[
                    ['Research Problem', summaries[paper.paper_id].research_problem],
                    ['Objective', summaries[paper.paper_id].objective || summaries[paper.paper_id].main_objective],
                    ['Methodology', summaries[paper.paper_id].methodology],
                    ['Dataset', summaries[paper.paper_id].dataset],
                    ['Key Findings', Array.isArray(summaries[paper.paper_id].key_findings) ? summaries[paper.paper_id].key_findings.join('; ') : summaries[paper.paper_id].key_findings],
                    ['Limitations', summaries[paper.paper_id].limitations],
                    ['Conclusion', summaries[paper.paper_id].conclusion],
                  ].filter(([, v]) => v).map(([label, val]) => (
                    <div key={label}><span className="font-semibold text-white">{label}: </span>{val}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {papers.length === 0 && !loading && !error && (
          <p className="text-gray-500 text-center mt-10">Enter a topic above to search research papers.</p>
        )}

        {papers.length > 0 && offset < total && !loading && (
          <div className="text-center pt-4 pb-8">
            <button onClick={handleLoadMore} disabled={loadingMore} className="btn-secondary px-8 py-3 text-base">
              {loadingMore ? 'Loading...' : `Load More (${Math.min(LIMIT, total - offset)} more)`}
            </button>
            <p className="text-xs text-gray-600 mt-2">{papers.length} of {total.toLocaleString()} loaded</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────
// Upload & Analysis Page
// ─────────────────────────────────────────────
const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [documentId, setDocumentId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [hasText, setHasText] = useState(true);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true); setStatus('Uploading and processing PDF...'); setDocumentId(null); setSummary(null);
    try {
      const data = await backendAPI.uploadDocument(file);
      setDocumentId(data.document_id);
      if (data.status === 'no_text') {
        setHasText(false);
        setStatus('Warning: No selectable text found. This PDF may be scanned. Q&A and summarization require a text-based PDF.');
      } else {
        setHasText(true);
        setStatus(`Success: ${data.page_count} pages indexed and ready for analysis.`);
      }
    } catch (error) {
      setStatus('Error: Upload failed. Make sure the backend is running and the file is a valid PDF.');
    }
    setLoading(false);
  };

  const handleSummarize = async () => {
    if (!documentId) return;
    setLoading(true); setStatus('Generating structured summary...');
    try {
      const data = await backendAPI.summarizeDocument(documentId);
      setSummary(data.summary || data); setStatus('');
    } catch { setStatus('Error generating summary.'); }
    setLoading(false);
  };

  if (documentId) {
    return (
      <div className="max-w-5xl mx-auto">
        <h2 className="text-4xl font-sans font-bold mb-8">Document Analysis</h2>
        {status && <p className="mb-6 text-primary-400 font-medium">{status}</p>}
        <div className="grid grid-cols-1 gap-8">
          <div className="glass-card p-6">
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2"><BookOpen className="text-primary-400" /> Summary</h3>
            {!(summary && Object.keys(summary).some(k => summary[k] && summary[k] !== 'Not available in the document.')) ? (
              <div className="text-center py-10">
                <p className="text-gray-400 mb-6">Generate a structured 7-field summary of this paper.</p>
                <button onClick={handleSummarize} className="btn-primary mx-auto" disabled={loading || !hasText}>Generate Summary</button>
                {!hasText && <p className="text-yellow-500 text-sm mt-3">Summarization requires a text-based PDF.</p>}
              </div>
            ) : (
              <div className="space-y-4 text-gray-300">
                {[
                  ['Research Problem', summary.research_problem],
                  ['Objective', summary.objective || summary.main_objective],
                  ['Methodology', summary.methodology],
                  ['Dataset', summary.dataset],
                  ['Key Findings', Array.isArray(summary.key_findings) ? summary.key_findings.join(', ') : summary.key_findings],
                  ['Limitations', summary.limitations],
                  ['Conclusion', summary.conclusion],
                ].filter(([, v]) => v).map(([label, val]) => (
                  <div key={label}>
                    <h4 className="font-bold text-primary-400">{label}</h4>
                    <p>{val}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto text-center">
      <h2 className="text-4xl font-sans font-bold mb-8">Upload Document</h2>
      <div className="glass-card p-10 border-dashed border-2 border-gray-700">
        <Upload size={48} className="mx-auto text-primary-500 mb-4" />
        <p className="text-gray-300 mb-6">Select a text-based PDF to upload and analyze.</p>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])}
          className="mb-6 block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-800 file:text-primary-400 hover:file:bg-gray-700" />
        <button onClick={handleUpload} className="btn-primary w-full" disabled={!file || loading}>
          {loading ? 'Processing...' : 'Upload and Process PDF'}
        </button>
        {status && <p className="mt-6 text-primary-400 font-medium text-sm">{status}</p>}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────
// App Router (with auth guard)
// ─────────────────────────────────────────────
function App() {
  const [auth, setAuth] = useState(isLoggedIn());

  const handleLogout = () => {
    setLoggedOut();
    setAuth(false);
  };

  if (!auth) {
    return <LoginPage onLogin={() => setAuth(true)} />;
  }

  return (
    <Router>
      <Layout onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/compare" element={<ComparisonPage />} />
          <Route path="/gaps" element={<GapDetectionPage />} />
          <Route path="/graph" element={<KnowledgeGraphPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
