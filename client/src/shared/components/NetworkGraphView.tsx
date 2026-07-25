import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import clsx from 'clsx';
import type { NetworkEdge, NetworkNode } from 'shared/api';

interface SimulationNode extends NetworkNode, d3.SimulationNodeDatum {
  fx?: number | null;
  fy?: number | null;
}

type SimulationLink = Omit<NetworkEdge, 'source' | 'target'> & d3.SimulationLinkDatum<SimulationNode>;

interface NetworkGraphViewProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  width?: number;
  height?: number;
  className?: string;
  onNodeClick?: (node: NetworkNode) => void;
  highlightedIds?: Set<string> | string[];
  onNodeSelect?: (node: NetworkNode | null) => void;
  selectedIds?: Set<string> | string[];
  onToggleNeighborhood?: (nodeId: string) => void;
  expandedNodes?: Set<string>;
}

const TYPE_COLORS: Record<string, string> = {
  Offender: '#dc2626',
  Crime: '#ea580c',
  FIR: '#ca8a04',
  District: '#2563eb',
  PoliceStation: '#059669',
  Officer: '#7c3aed',
  Vehicle: '#0891b2',
  Victim: '#db2777',
  Location: '#d97706',
};

const EDGE_COLORS: Record<string, string> = {
  co_offender: '#dc2626',
  family: '#7c3aed',
  phone: '#0891b2',
  vehicle: '#059669',
  financial: '#d97706',
  location: '#2563eb',
  suspect: '#ea580c',
  witness: '#059669',
  acquaintance: '#64748b',
  unknown: '#94a3b8',
  committed: '#dc2626',
  registered_in: '#ca8a04',
  investigated_by: '#7c3aed',
  occurred_at: '#2563eb',
  belongs_to: '#64748b',
  related_to: '#d97706',
  operates_in: '#0891b2',
  known_at: '#059669',
  uses: '#db2777',
};

const RISK_COLORS: Record<string, string> = {
  Critical: '#dc2626',
  High: '#ea580c',
  Medium: '#ca8a04',
  Low: '#10b981',
};

function getNodeRadius(d: SimulationNode, degreeMap: Map<string, number>): number {
  const isCluster = (d.properties?.isCluster as boolean | undefined) || false;
  if (isCluster) {
    const count = (d.properties?.memberCount as number) || 1;
    return Math.max(22, Math.sqrt(count) * 3.5 + 16);
  }
  const degree = degreeMap.get(d.id) || 0;
  const baseRadius = Math.max(9, Math.min(30, Math.sqrt(degree) * 5.5 + 9));
  const riskLevel = d.properties?.risk_level as string | undefined;
  if (riskLevel === 'Critical') return baseRadius + 5;
  if (riskLevel === 'High') return baseRadius + 3;
  if (riskLevel === 'Medium') return baseRadius + 1;
  return baseRadius;
}

function getEdgePath(
  d: SimulationLink,
  pairTotal: Map<string, number>,
): string {
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
  const offset = total > 1 ? (idx - (total - 1) / 2) * 24 : 0;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const midX = (sx + tx) / 2 + nx * offset;
  const midY = (sy + ty) / 2 + ny * offset;
  return `M${sx} ${sy} Q${midX} ${midY} ${tx} ${ty}`;
}

const SIMULATION_CONFIG = {
  chargeStrength: -600,
  chargeDistanceMax: 600,
  linkDistanceBase: 140,
  linkDistanceOffender: 110,
  linkDistanceOther: 170,
  linkStrength: 0.45,
  collidePadding: 10,
  xStrength: 0.12,
  yStrength: 0.12,
  alphaDecay: 0.018,
  velocityDecay: 0.28,
  minZoom: 0.08,
  maxZoom: 10,
};

const NetworkGraphView: React.FC<NetworkGraphViewProps> = ({
  nodes,
  edges,
  width = 900,
  height = 600,
  className,
  onNodeClick,
  highlightedIds,
  onNodeSelect,
  selectedIds,
  onToggleNeighborhood,
  expandedNodes,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const linkRef = useRef<d3.Selection<SVGPathElement, SimulationLink, SVGGElement, unknown> | null>(null);
  const nodeRef = useRef<d3.Selection<SVGCircleElement, SimulationNode, SVGGElement, unknown> | null>(null);
  const labelRef = useRef<d3.Selection<SVGTextElement, SimulationNode, SVGGElement, unknown> | null>(null);
  const onNodeClickRef = useRef(onNodeClick);
  const onNodeSelectRef = useRef(onNodeSelect);
  const degreeMapRef = useRef<Map<string, number>>(new Map());
  const neighborMapRef = useRef<Map<string, Set<string>>>(new Map());
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const dragNodeRef = useRef<SimulationNode | null>(null);

  useEffect(() => {
    onNodeClickRef.current = onNodeClick;
  }, [onNodeClick]);

  useEffect(() => {
    onNodeSelectRef.current = onNodeSelect;
  }, [onNodeSelect]);

  const highlightedSet = useMemo(() => {
    if (!highlightedIds) return new Set<string>();
    return highlightedIds instanceof Set ? highlightedIds : new Set(highlightedIds);
  }, [highlightedIds]);

  const selectedSet = useMemo(() => {
    if (!selectedIds) return new Set<string>();
    return selectedIds instanceof Set ? selectedIds : new Set(selectedIds);
  }, [selectedIds]);

  const multiSelected = selectedSet.size > 1;

  const effectiveNodes = useMemo(() => {
    if (!expandedNodes || expandedNodes.size === 0) return nodes;
    const visible = new Set<string>();
    for (const expandedId of expandedNodes) {
      const neighbors = neighborMapRef.current.get(expandedId);
      if (neighbors) {
        visible.add(expandedId);
        neighbors.forEach((n) => visible.add(n));
      }
    }
    return nodes.filter((n) => visible.has(n.id));
  }, [nodes, expandedNodes]);

  const effectiveEdges = useMemo(() => {
    const visible = new Set(effectiveNodes.map((n) => n.id));
    return edges.filter((e) => {
      const sid = String((e.source as any)?.id ?? e.source);
      const tid = String((e.target as any)?.id ?? e.target);
      return visible.has(sid) && visible.has(tid);
    });
  }, [edges, effectiveNodes]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0 || !containerRef.current) return;

    const container = containerRef.current;
    const containerWidth = container.clientWidth || width;
    const containerHeight = container.clientHeight || height;
    const w = Math.max(containerWidth, 600);
    const h = Math.max(containerHeight, 500);

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simulationNodes: SimulationNode[] = nodes.map((n) => ({
      ...n,
      x: (n.properties?.x as number | undefined) ?? w / 2 + (Math.random() - 0.5) * 300,
      y: (n.properties?.y as number | undefined) ?? h / 2 + (Math.random() - 0.5) * 300,
    }));

    const simulationLinks: SimulationLink[] = edges.map((e) => ({ ...e }));

    const degreeMap = new Map<string, number>();
    const neighborMap = new Map<string, Set<string>>();
    for (const n of simulationNodes) {
      degreeMap.set(n.id, 0);
      neighborMap.set(n.id, new Set());
    }
    simulationLinks.forEach((l) => {
      const sid = String((l.source as unknown) as string);
      const tid = String((l.target as unknown) as string);
      if (sid && tid) {
        degreeMap.set(sid, (degreeMap.get(sid) || 0) + 1);
        degreeMap.set(tid, (degreeMap.get(tid) || 0) + 1);
        neighborMap.get(sid)?.add(tid);
        neighborMap.get(tid)?.add(sid);
      }
    });
    degreeMapRef.current = degreeMap;
    neighborMapRef.current = neighborMap;

    const pairTotal = new Map<string, number>();
    simulationLinks.forEach((l) => {
      const sid = String((l.source as unknown) as string);
      const tid = String((l.target as unknown) as string);
      const key = [sid, tid].sort().join('|');
      pairTotal.set(key, (pairTotal.get(key) || 0) + 1);
    });

    const pairSeen = new Map<string, number>();
    simulationLinks.forEach((l) => {
      const sid = String((l.source as unknown) as string);
      const tid = String((l.target as unknown) as string);
      const key = [sid, tid].sort().join('|');
      (l as any).pairIndex = pairSeen.get(key) || 0;
      pairSeen.set(key, (pairSeen.get(key) || 0) + 1);
    });

    const types = Array.from(new Set(simulationNodes.map((n) => n.type)));
    const angleStep = (2 * Math.PI) / Math.max(types.length, 1);
    const clusterRadius = Math.min(w, h) * 0.32;
    const clusterCenter: Record<string, { x: number; y: number }> = {};
    types.forEach((type, i) => {
      const angle = angleStep * i - Math.PI / 2;
      clusterCenter[type] = {
        x: w / 2 + clusterRadius * Math.cos(angle),
        y: h / 2 + clusterRadius * Math.sin(angle),
      };
    });

    const simulation = d3
      .forceSimulation<SimulationNode>(simulationNodes)
      .force(
        'link',
        d3
          .forceLink<SimulationNode, SimulationLink>(simulationLinks)
          .id((d) => d.id)
          .distance((l) => {
            const sType = (l.source as SimulationNode).type;
            const tType = (l.target as SimulationNode).type;
            if (sType === 'Offender' && tType === 'Offender') return 130;
            if (sType === 'Offender' && tType === 'Crime') return 105;
            if (sType === 'Offender' || tType === 'Offender') return 110;
            return 155;
          })
          .strength(SIMULATION_CONFIG.linkStrength),
      )
      .force('charge', d3.forceManyBody<SimulationNode>().strength(SIMULATION_CONFIG.chargeStrength).distanceMax(SIMULATION_CONFIG.chargeDistanceMax))
      .force('center', d3.forceCenter(w / 2, h / 2))
      .force(
        'collide',
        d3.forceCollide<SimulationNode>((d) => getNodeRadius(d, degreeMap) + SIMULATION_CONFIG.collidePadding).strength(0.85),
      )
      .force(
        'x',
        d3.forceX<SimulationNode>((d) => clusterCenter[d.type]?.x ?? w / 2).strength(SIMULATION_CONFIG.xStrength),
      )
      .force(
        'y',
        d3.forceY<SimulationNode>((d) => clusterCenter[d.type]?.y ?? h / 2).strength(SIMULATION_CONFIG.yStrength),
      )
      .alphaDecay(SIMULATION_CONFIG.alphaDecay)
      .alphaTarget(0)
      .velocityDecay(SIMULATION_CONFIG.velocityDecay);

    const g = svg.append('g').attr('class', 'graph-content');

    const zoomBehavior = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([SIMULATION_CONFIG.minZoom, SIMULATION_CONFIG.maxZoom])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        setZoomLevel(event.transform.k);
      });
    zoomBehaviorRef.current = zoomBehavior;
    svg.call(zoomBehavior);

    svg.insert('rect', ':first-child')
      .attr('width', w)
      .attr('height', h)
      .attr('fill', 'transparent')
      .on('click', (event) => {
        if ((event.target as SVGElement).tagName === 'rect') {
          setActiveNodeId(null);
          onNodeSelectRef.current?.(null);
          svg.transition().duration(300).call(zoomBehavior.transform, d3.zoomIdentity);
        }
      });

    const linkSel = g
      .append('g')
      .attr('class', 'links')
      .selectAll<SVGPathElement, SimulationLink>('path')
      .data(simulationLinks)
      .join('path')
      .attr('fill', 'none')
      .attr('stroke', (d) => EDGE_COLORS[d.type || 'unknown'] || EDGE_COLORS['unknown'])
      .attr('stroke-opacity', 0.5)
      .attr('stroke-width', (d) => {
        const sId = String((d.source as unknown) as string);
        const tId = String((d.target as unknown) as string);
        const sDeg = degreeMap.get(sId) || 0;
        const tDeg = degreeMap.get(tId) || 0;
        return Math.max(1.2, Math.min(4.5, (sDeg + tDeg) / 3.5));
      })
      .attr('stroke-dasharray', (d) => {
        const edgeType = d.type || '';
        if (edgeType === 'family') return '7,4';
        if (edgeType === 'financial') return '5,5';
        if (edgeType === 'same_phone') return '3,3';
        if (edgeType === 'same_vehicle') return '6,3';
        return 'none';
      });

    const nodeSel = g
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGCircleElement, SimulationNode>('circle')
      .data(simulationNodes)
      .join('circle')
      .attr('r', (d) => getNodeRadius(d, degreeMap))
      .attr('fill', (d) => {
        const riskLevel = d.properties?.risk_level as string | undefined;
        if (riskLevel && RISK_COLORS[riskLevel]) return RISK_COLORS[riskLevel];
        if (d.properties?.isCluster) return '#6366f1';
        return TYPE_COLORS[d.type] || '#64748b';
      })
      .attr('stroke', (d) => {
        if (activeNodeId && d.id === activeNodeId) return '#fbbf24';
        if (selectedSet.has(d.id)) return '#fbbf24';
        if (highlightedSet.has(d.id)) return '#fbbf24';
        return '#ffffff';
      })
      .attr('stroke-width', (d) => {
        if (activeNodeId && d.id === activeNodeId) return 5;
        if (selectedSet.has(d.id)) return 4.5;
        if (highlightedSet.has(d.id)) return 4;
        return 2.2;
      })
      .attr('cursor', 'pointer')
      .attr('opacity', (d) => {
        if (highlightedSet.size > 0 && !highlightedSet.has(d.id)) return 0.12;
        return 1;
      })
      .on('mouseenter', (_, d) => {
        setHoveredNodeId(d.id);
        labelRef.current?.selectAll<SVGTextElement, SimulationNode>('text').style('opacity', (l) =>
          l.id === d.id ? 1 : (degreeMap.get(d.id) || 0) > 4 ? 0.65 : 0.08,
        );
      })
      .on('mouseleave', () => {
        setHoveredNodeId(null);
      })
      .on('click', (event, d) => {
        event.stopPropagation();
        if (event.shiftKey) {
          const newSelected = new Set(selectedSet);
          if (newSelected.has(d.id)) {
            newSelected.delete(d.id);
          } else {
            newSelected.add(d.id);
          }
          onNodeSelectRef.current?.(nodes.find((n) => newSelected.has(n.id)) || null);
        } else {
          setActiveNodeId((prev) => (prev === d.id ? null : d.id));
          onNodeSelectRef.current?.(d);
          onNodeClickRef.current?.(d);
        }
      })
      .on('dblclick', (_, d) => {
        const svgEl = svgRef.current;
        const zoom = zoomBehaviorRef.current;
        if (!svgEl || !zoom) return;
        const gEl = d3.select<SVGGElement, any>(svgEl).select('.graph-content');
        const bounds = (gEl.node() as unknown as SVGGElement)?.getBBox();
        if (!bounds) return;
        const midX = (d.x ?? w / 2);
        const midY = (d.y ?? h / 2);
        const scale = 1.8;
        const transform = d3.zoomIdentity.translate(w / 2 - midX * scale, h / 2 - midY * scale).scale(scale);
        d3.select(svgEl).transition().duration(500).call((zoom as any).transform, transform);
      })
      .call(
        d3
          .drag<SVGCircleElement, SimulationNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
            dragNodeRef.current = d;
            setIsDragging(true);
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
            dragNodeRef.current = null;
            setIsDragging(false);
          }),
      );

    const labelSel = g
      .append('g')
      .attr('class', 'labels')
      .selectAll<SVGTextElement, SimulationNode>('text')
      .data(simulationNodes)
      .join('text')
      .text((d) => d.label)
      .attr('font-size', (d) => (d.properties?.isCluster ? 12 : 10.5))
      .attr('font-weight', (d) => (d.properties?.isCluster ? 'bold' : 'normal'))
      .attr('dx', 15)
      .attr('dy', 4.5)
      .attr('fill', '#1e293b')
      .style('pointer-events', 'none')
      .style('text-shadow', '0 1px 3px rgba(255,255,255,0.95), -1px 0 3px rgba(255,255,255,0.7)')
      .style('paint-order', 'stroke fill')
      .style('opacity', 0);

    linkRef.current = linkSel;
    nodeRef.current = nodeSel;
    labelRef.current = labelSel;

    simulation.on('tick', () => {
      linkRef.current?.attr('d', (d) => getEdgePath(d, pairTotal));
      nodeRef.current?.attr('cx', (d) => d.x ?? 0).attr('cy', (d) => d.y ?? 0);
      labelRef.current?.attr('x', (d) => (d.x ?? 0) + 15).attr('y', (d) => (d.y ?? 0) + 4.5);
    });

    const gBounds = g.node()?.getBBox();
    if (gBounds && gBounds.width > 0 && gBounds.height > 0) {
      const scale = 0.82 / Math.max(gBounds.width / w, gBounds.height / h);
      const midX = gBounds.x + gBounds.width / 2;
      const midY = gBounds.y + gBounds.height / 2;
      const transform = d3.zoomIdentity.translate(w / 2 - midX * scale, h / 2 - midY * scale).scale(scale);
      svg.transition().duration(800).call(zoomBehavior.transform, transform);
    }

    return () => {
      simulation.stop();
    };
  }, [effectiveNodes, effectiveEdges, width, height, highlightedSet, selectedSet]);

  useEffect(() => {
    if (!nodeRef.current || !linkRef.current || !labelRef.current) return;
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
      if (highlightedSet.size > 0 && !highlightedSet.has(d.id)) return 0.1;
      if (active && !multiSelected) return d.id === active || neighbors.has(d.id) ? 1 : 0.05;
      if (multiSelected && selectedSet.size > 0) {
        return selectedSet.has(d.id) ? 1 : 0.07;
      }
      return 1;
    });

    nodeRef.current.attr('stroke', (d) => {
      if (multiSelected && selectedSet.has(d.id)) return '#fbbf24';
      if (active && d.id === active) return '#fbbf24';
      if (highlightedSet.has(d.id)) return '#fbbf24';
      if (hoveredNodeId && d.id === hoveredNodeId) return '#fbbf24';
      return '#ffffff';
    });

    nodeRef.current.attr('stroke-width', (d) => {
      if (multiSelected && selectedSet.has(d.id)) return 5;
      if (active && d.id === active) return 5;
      if (hoveredNodeId && d.id === hoveredNodeId) return 4;
      if (highlightedSet.has(d.id)) return 4;
      return 2.2;
    });

    nodeRef.current.attr('filter', (d) => {
      if (active && d.id === active) return 'url(#glow-active)';
      if (hoveredNodeId && d.id === hoveredNodeId) return 'url(#glow-hover)';
      return 'none';
    });

    linkRef.current.attr('stroke-opacity', (d) => {
      const s = d.source as unknown as SimulationNode;
      const t = d.target as unknown as SimulationNode;
      if (active && !multiSelected) return s.id === active || t.id === active ? 0.95 : 0.015;
      if (multiSelected && selectedSet.size > 0) {
        return selectedSet.has(s.id) && selectedSet.has(t.id) ? 0.85 : 0.015;
      }
      if (highlightedSet.size > 0) {
        return highlightedSet.has(s.id) && highlightedSet.has(t.id) ? 0.75 : 0.02;
      }
      return 0.45;
    });

    labelRef.current.style('opacity', (d) => {
      if (multiSelected && selectedSet.has(d.id)) return 1;
      if (active && !multiSelected) return d.id === active || neighbors.has(d.id) ? 1 : 0.02;
      if (highlightedSet.size > 0) return highlightedSet.has(d.id) ? 1 : 0.02;
      const deg = degreeMapRef.current.get(d.id) || 0;
      if (zoomLevel < 0.5) return deg > 10 ? 0.9 : 0;
      if (zoomLevel < 0.8) return deg > 6 ? 0.85 : 0;
      if (zoomLevel < 1.2) return deg > 3 ? 0.7 : 0;
      const isCluster = d.properties?.isCluster;
      return isCluster ? 1 : deg > 2 ? 0.6 : 0;
    });
  }, [activeNodeId, hoveredNodeId, highlightedSet, selectedSet, multiSelected, edges, zoomLevel]);

  const fitToScreen = useCallback(() => {
    const zoom = zoomBehaviorRef.current;
    if (!svgRef.current || !zoom) return;
    const g = d3.select<SVGGElement, any>(svgRef.current).select('.graph-content');
    const bounds = (g.node() as unknown as SVGGElement)?.getBBox();
    if (!bounds || !bounds.width || !bounds.height) return;
    const w = containerRef.current?.clientWidth || width;
    const h = containerRef.current?.clientHeight || height;
    const midX = bounds.x + bounds.width / 2;
    const midY = bounds.y + bounds.height / 2;
    const scale = 0.82 / Math.max(bounds.width / w, bounds.height / h);
    const transform = d3.zoomIdentity.translate(w / 2 - midX * scale, h / 2 - midY * scale).scale(scale);
    (d3.select(svgRef.current) as any).transition().duration(750).call((zoom as any).transform, transform);
  }, [width, height]);

  const zoomIn = useCallback(() => {
    const zoom = zoomBehaviorRef.current;
    if (!svgRef.current || !zoom) return;
    (d3.select(svgRef.current) as any).transition().duration(300).call((zoom as any).scaleBy, 1.5);
  }, []);

  const zoomOut = useCallback(() => {
    const zoom = zoomBehaviorRef.current;
    if (!svgRef.current || !zoom) return;
    (d3.select(svgRef.current) as any).transition().duration(300).call((zoom as any).scaleBy, 0.67);
  }, []);

  const zoomReset = useCallback(() => {
    const zoom = zoomBehaviorRef.current;
    if (!svgRef.current || !zoom) return;
    (d3.select(svgRef.current) as any).transition().duration(500).call((zoom as any).transform, d3.zoomIdentity);
    setZoomLevel(1);
  }, []);

  const toggleNeighborhood = useCallback(
    (nodeId: string) => {
      if (onToggleNeighborhood) {
        onToggleNeighborhood(nodeId);
      }
    },
    [onToggleNeighborhood],
  );

  const types = useMemo(() => Array.from(new Set(nodes.map((n) => n.type))), [nodes]);
  const typeCounts = useMemo(() => {
    const counts = new Map<string, number>();
    nodes.forEach((n) => counts.set(n.type, (counts.get(n.type) || 0) + 1));
    return counts;
  }, [nodes]);

  const edgeTypes = useMemo(() => {
    const types = new Set<string>();
    edges.forEach((e) => {
      if (e.type) types.add(e.type);
    });
    return Array.from(types).sort();
  }, [edges]);

  const degreeStats = useMemo(() => {
    const degs = Array.from(degreeMapRef.current.values());
    if (!degs.length) return { max: 0, avg: 0, min: 0 };
    return {
      max: Math.max(...degs),
      avg: (degs.reduce((a, b) => a + b, 0) / degs.length).toFixed(1),
      min: Math.min(...degs),
    };
  }, []);

  return (
    <div ref={containerRef} className={clsx('relative w-full h-full min-h-[650px]', className)}>
      <svg ref={svgRef} className="h-full w-full" viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <filter id="glow-active" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#fbbf24" floodOpacity="0.7" />
          </filter>
          <filter id="glow-hover" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#fbbf24" floodOpacity="0.5" />
          </filter>
        </defs>
      </svg>
      <div className="absolute top-3 left-3 flex flex-col gap-1.5 z-10">
        <button type="button" onClick={zoomIn} className="rounded-lg bg-white/95 px-2.5 py-2 text-sm font-semibold shadow-lg hover:bg-gray-100 border border-gray-200" title="Zoom In">+</button>
        <button type="button" onClick={zoomOut} className="rounded-lg bg-white/95 px-2.5 py-2 text-sm font-semibold shadow-lg hover:bg-gray-100 border border-gray-200" title="Zoom Out">−</button>
        <button type="button" onClick={fitToScreen} className="rounded-lg bg-white/95 px-2.5 py-2 text-sm font-semibold shadow-lg hover:bg-gray-100 border border-gray-200" title="Fit to Screen">⊞</button>
        <button type="button" onClick={zoomReset} className="rounded-lg bg-white/95 px-2.5 py-2 text-sm font-semibold shadow-lg hover:bg-gray-100 border border-gray-200" title="Reset View">⟲</button>
      </div>
      <div className="absolute bottom-3 left-3 rounded-xl bg-white/95 p-4 shadow-xl z-10 text-xs max-w-xs border border-gray-200">
        <div className="font-semibold text-gray-800 mb-2">Node Types</div>
        {types.map((t) => (
          <div key={t} className="flex items-center gap-2 mb-1.5">
            <span className="inline-block h-3.5 w-3.5 rounded-full shadow-sm" style={{ backgroundColor: TYPE_COLORS[t] || '#64748b' }} />
            <span className="text-gray-700 font-medium">{t}</span>
            <span className="text-gray-400 ml-auto font-mono">{typeCounts.get(t)}</span>
          </div>
        ))}
        {edgeTypes.length > 0 && (
          <>
            <div className="mt-3 font-semibold text-gray-800 mb-1.5">Relationships</div>
            {edgeTypes.map((t) => (
              <div key={t} className="flex items-center gap-2 mb-1.5">
                <span className="inline-block h-2.5 w-5 rounded" style={{ backgroundColor: EDGE_COLORS[t] || '#94a3b8' }} />
                <span className="text-gray-700 capitalize">{t.replace(/_/g, ' ')}</span>
              </div>
            ))}
          </>
        )}
        <div className="mt-3 pt-2.5 border-t border-gray-200 text-gray-500 font-mono space-y-0.5">
          <div>Zoom: {(zoomLevel * 100).toFixed(0)}%</div>
          <div>Nodes: {nodes.length} | Edges: {edges.length}</div>
          <div>Max Degree: {degreeStats.max} | Avg: {degreeStats.avg}</div>
        </div>
      </div>
      {activeNodeId && (
        <div className="absolute top-3 right-3 z-10">
          <button
            type="button"
            onClick={() => toggleNeighborhood(activeNodeId)}
            className="rounded-lg bg-indigo-50 px-3 py-2 shadow-lg text-xs font-medium text-indigo-700 border border-indigo-200 hover:bg-indigo-100"
          >
            {expandedNodes?.has(activeNodeId) ? 'Collapse Neighbourhood' : 'Expand Neighbourhood'}
          </button>
        </div>
      )}
      {isDragging && (
        <div className="absolute top-3 right-3 rounded-lg bg-blue-50 px-3 py-1.5 shadow-lg z-10 text-xs text-blue-700 border border-blue-200">
          Dragging node...
        </div>
      )}
      <div className="absolute bottom-3 right-3 rounded-lg bg-white/95 p-3 shadow-lg z-10 text-xs border border-gray-200">
        <div className="font-semibold text-gray-700 mb-1">Risk Levels</div>
        {Object.entries(RISK_COLORS).map(([level, color]) => (
          <div key={level} className="flex items-center gap-2 mb-1">
            <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-gray-600">{level}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NetworkGraphView;
