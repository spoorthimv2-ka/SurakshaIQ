import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import clsx from 'clsx';
import type { NetworkEdge, NetworkNode } from 'shared/api';

interface SimulationNode extends NetworkNode, d3.SimulationNodeDatum {}

type SimulationLink = Omit<NetworkEdge, 'source' | 'target'> & d3.SimulationLinkDatum<SimulationNode>;

interface NetworkGraphViewProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  width?: number;
  height?: number;
  className?: string;
  onNodeClick?: (node: NetworkNode) => void;
  highlightedIds?: Set<string> | string[];
}

const TYPE_COLORS: Record<string, string> = {
  Offender: '#ef4444',
  Crime: '#f97316',
  FIR: '#eab308',
  District: '#3b82f6',
  PoliceStation: '#10b981',
  Officer: '#8b5cf6',
  Vehicle: '#06b6d4',
  Victim: '#ec4899',
  Location: '#f59e0b',
};

function getNodeRadius(d: SimulationNode, degreeMap: Map<string, number>): number {
  const isCluster = (d.properties?.isCluster as boolean | undefined) || false;
  if (isCluster) {
    const count = (d.properties?.memberCount as number) || 1;
    return Math.max(18, Math.sqrt(count) * 3 + 12);
  }
  const degree = degreeMap.get(d.id) || 0;
  return Math.max(6, Math.min(22, Math.sqrt(degree) * 5 + 6));
}

function getEdgePath(d: SimulationLink, pairTotal: Map<string, number>): string {
  const s = d.source as unknown as SimulationNode;
  const t = d.target as unknown as SimulationNode;
  const sx = s.x ?? 0;
  const sy = s.y ?? 0;
  const tx = t.x ?? 0;
  const ty = t.y ?? 0;
  const dx = tx - sx;
  const dy = ty - sy;
  const key = [s.id, t.id].sort().join('|');
  const total = pairTotal.get(key) || 1;
  const idx = (d as any).pairIndex || 0;
  const offset = (idx - (total - 1) / 2) * 18;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const midX = (sx + tx) / 2 + nx * offset;
  const midY = (sy + ty) / 2 + ny * offset;
  return `M${sx} ${sy} Q${midX} ${midY} ${tx} ${ty}`;
}

const NetworkGraphView: React.FC<NetworkGraphViewProps> = ({
  nodes,
  edges,
  width = 800,
  height = 500,
  className,
  onNodeClick,
  highlightedIds,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const linkRef = useRef<d3.Selection<SVGPathElement, SimulationLink, SVGGElement, unknown> | null>(null);
  const nodeRef = useRef<d3.Selection<SVGCircleElement, SimulationNode, SVGGElement, unknown> | null>(null);
  const labelRef = useRef<d3.Selection<SVGTextElement, SimulationNode, SVGGElement, unknown> | null>(null);
  const onNodeClickRef = useRef(onNodeClick);
  const degreeMapRef = useRef<Map<string, number>>(new Map());
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);

  useEffect(() => {
    onNodeClickRef.current = onNodeClick;
  }, [onNodeClick]);

  const highlightedSet = useMemo(() => {
    if (!highlightedIds) return new Set<string>();
    return highlightedIds instanceof Set ? highlightedIds : new Set(highlightedIds);
  }, [highlightedIds]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simulationNodes: SimulationNode[] = nodes.map((n) => ({
      ...n,
      x: (n.properties?.x as number | undefined) ?? width / 2 + (Math.random() - 0.5) * 300,
      y: (n.properties?.y as number | undefined) ?? height / 2 + (Math.random() - 0.5) * 300,
    }));

    const simulationLinks: SimulationLink[] = edges.map((e) => ({ ...e }));

    const degreeMap = new Map<string, number>();
    simulationLinks.forEach((l) => {
      const sid = (l.source as unknown) as string;
      const tid = (l.target as unknown) as string;
      degreeMap.set(sid, (degreeMap.get(sid) || 0) + 1);
      degreeMap.set(tid, (degreeMap.get(tid) || 0) + 1);
    });
    degreeMapRef.current = degreeMap;

    const pairTotal = new Map<string, number>();
    simulationLinks.forEach((l) => {
      const sid = (l.source as unknown) as string;
      const tid = (l.target as unknown) as string;
      const key = [sid, tid].sort().join('|');
      pairTotal.set(key, (pairTotal.get(key) || 0) + 1);
    });

    const pairSeen = new Map<string, number>();
    simulationLinks.forEach((l) => {
      const sid = (l.source as unknown) as string;
      const tid = (l.target as unknown) as string;
      const key = [sid, tid].sort().join('|');
      (l as any).pairIndex = pairSeen.get(key) || 0;
      pairSeen.set(key, (pairSeen.get(key) || 0) + 1);
    });

    const types = Array.from(new Set(simulationNodes.map((n) => n.type)));
    const angleStep = (2 * Math.PI) / types.length;
    const clusterRadius = Math.min(width, height) * 0.3;
    const clusterCenter: Record<string, { x: number; y: number }> = {};
    types.forEach((type, i) => {
      const angle = angleStep * i;
      clusterCenter[type] = {
        x: width / 2 + clusterRadius * Math.cos(angle),
        y: height / 2 + clusterRadius * Math.sin(angle),
      };
    });

    const simulation = d3
      .forceSimulation<SimulationNode>(simulationNodes)
      .force(
        'link',
        d3
          .forceLink<SimulationNode, SimulationLink>(simulationLinks)
          .id((d) => d.id)
          .distance(120)
          .strength(0.4),
      )
      .force('charge', d3.forceManyBody<SimulationNode>().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force(
        'collide',
        d3.forceCollide<SimulationNode>((d) => getNodeRadius(d, degreeMap) + 3).strength(0.8),
      )
      .force(
        'x',
        d3.forceX<SimulationNode>((d) => clusterCenter[d.type]?.x ?? width / 2).strength(0.12),
      )
      .force(
        'y',
        d3.forceY<SimulationNode>((d) => clusterCenter[d.type]?.y ?? height / 2).strength(0.12),
      );

    const g = svg.append('g').attr('class', 'graph-content');

    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    zoomBehaviorRef.current = zoomBehavior;
    svg.call(zoomBehavior);

    svg.insert('rect', ':first-child')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'transparent')
      .on('click', () => {
        setActiveNodeId(null);
        svg.transition().duration(300).call(zoomBehavior.transform, d3.zoomIdentity);
      });

    const linkSel = g
      .append('g')
      .selectAll<SVGPathElement, SimulationLink>('path')
      .data(simulationLinks)
      .join('path')
      .attr('fill', 'none')
      .attr('stroke', '#94a3b8')
      .attr('stroke-opacity', 0.25)
      .attr('stroke-width', 1.5);

    const nodeSel = g
      .append('g')
      .selectAll<SVGCircleElement, SimulationNode>('circle')
      .data(simulationNodes)
      .join('circle')
      .attr('r', (d) => getNodeRadius(d, degreeMap))
      .attr('fill', (d) => TYPE_COLORS[d.type] || '#64748b')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1.5)
      .attr('cursor', 'pointer')
      .on('click', (_, d) => {
        setActiveNodeId((prev) => (prev === d.id ? null : d.id));
        onNodeClickRef.current?.(d);
      })
      .on('mouseenter', (_, d) => {
        labelRef.current?.selectAll<SVGTextElement, SimulationNode>('text').style('opacity', (l) => (l.id === d.id ? 1 : 0.6));
      })
      .on('mouseleave', () => {
        // visual update handled by activeNode/ highlight effect
      });

    const labelSel = g
      .append('g')
      .selectAll<SVGTextElement, SimulationNode>('text')
      .data(simulationNodes)
      .join('text')
      .text((d) => d.label)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4)
      .attr('fill', '#334155')
      .style('pointer-events', 'none');

    linkRef.current = linkSel;
    nodeRef.current = nodeSel;
    labelRef.current = labelSel;

    simulation.on('tick', () => {
      linkRef.current?.attr('d', (d) => getEdgePath(d, pairTotal));
      nodeRef.current?.attr('cx', (d) => d.x ?? 0).attr('cy', (d) => d.y ?? 0);
      labelRef.current?.attr('x', (d) => (d.x ?? 0) + 12).attr('y', (d) => (d.y ?? 0) + 4);
    });

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, width, height]);

  useEffect(() => {
    if (!linkRef.current || !nodeRef.current || !labelRef.current) return;
    const active = activeNodeId;
    const neighbors = new Set<string>();
    if (active) {
      edges.forEach((e) => {
        const sid = String((e.source as any)?.id ?? e.source);
        const tid = String((e.target as any)?.id ?? e.target);
        if (sid === active) neighbors.add(tid);
        if (tid === active) neighbors.add(sid);
      });
    }

    nodeRef.current.attr('opacity', (d) => {
      if (highlightedSet.size > 0 && !highlightedSet.has(d.id)) return 0.15;
      if (active) return d.id === active || neighbors.has(d.id) ? 1 : 0.08;
      return 1;
    });

    nodeRef.current.attr('stroke', (d) => {
      if (active && d.id === active) return '#fbbf24';
      if (highlightedSet.has(d.id)) return '#fbbf24';
      return '#ffffff';
    });

    nodeRef.current.attr('stroke-width', (d) => {
      if (active && d.id === active) return 4;
      if (highlightedSet.has(d.id)) return 4;
      return 1.5;
    });

    linkRef.current.attr('opacity', (d) => {
      const s = d.source as unknown as SimulationNode;
      const t = d.target as unknown as SimulationNode;
      if (active) return s.id === active || t.id === active ? 0.8 : 0.03;
      if (highlightedSet && highlightedSet.size > 0) {
        return highlightedSet.has(s.id) && highlightedSet.has(t.id) ? 0.6 : 0.04;
      }
      return 0.25;
    });

    labelRef.current.style('opacity', (d) => {
      if (active) return d.id === active || neighbors.has(d.id) ? 1 : 0.05;
      if (highlightedSet.size > 0) return highlightedSet.has(d.id) ? 1 : 0.05;
      const deg = degreeMapRef.current.get(d.id) || 0;
      return deg > 5 ? 1 : 0;
    });
  }, [activeNodeId, highlightedSet, edges]);

  const fitToScreen = useCallback(() => {
    const svg = d3.select(svgRef.current);
    const zoom = zoomBehaviorRef.current;
    if (!svgRef.current || !zoom) return;
    const g = svg.select<SVGGElement>('.graph-content');
    const bounds = g.node()?.getBBox();
    if (!bounds || !bounds.width || !bounds.height) return;
    const fullWidth = width;
    const fullHeight = height;
    const midX = bounds.x + bounds.width / 2;
    const midY = bounds.y + bounds.height / 2;
    const scale = 0.8 / Math.max(bounds.width / fullWidth, bounds.height / fullHeight);
    const transform = d3.zoomIdentity.translate(fullWidth / 2 - midX * scale, fullHeight / 2 - midY * scale).scale(scale);
    (svg.transition().duration(750) as any).call((zoom as any).transform, transform);
  }, [width, height]);

  return (
    <div className={clsx('relative', className)}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="h-full w-full"
        viewBox={`0 0 ${width} ${height}`}
      />
      <button
        type="button"
        onClick={fitToScreen}
        className="absolute top-2 right-2 rounded-md bg-white/90 px-2 py-1 text-xs shadow hover:bg-gray-100"
      >
        Fit to Screen
      </button>
    </div>
  );
};

export default NetworkGraphView;
