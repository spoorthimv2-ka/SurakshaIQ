import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import clsx from 'clsx';
import type { NetworkEdge, NetworkNode } from 'shared/api';

interface SimulationNode extends NetworkNode, d3.SimulationNodeDatum {}

type SimulationLink = d3.SimulationLinkDatum<SimulationNode> & NetworkEdge;

interface NetworkGraphViewProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  width?: number;
  height?: number;
  className?: string;
  onNodeClick?: (node: NetworkNode) => void;
}

const NetworkGraphView: React.FC<NetworkGraphViewProps> = ({
  nodes,
  edges,
  width = 640,
  height = 400,
  className,
  onNodeClick,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simulationNodes: SimulationNode[] = nodes.map((n) => ({ ...n }));

    const simulationLinks: SimulationLink[] = edges.map((e) => ({
      ...e,
    }));

    const simulation = d3
      .forceSimulation<SimulationNode>(simulationNodes)
      .force(
        'link',
        d3
          .forceLink<SimulationNode, SimulationLink>(simulationLinks)
          .id((d) => d.id)
          .distance(80)
      )
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .selectAll('line')
      .data(simulationLinks)
      .join('line')
      .attr('stroke', '#94a3b8')
      .attr('stroke-width', (d) => Math.max(1, d.weight));

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(simulationNodes)
      .join('circle')
      .attr('r', 10)
      .attr('fill', '#3b82f6')
      .attr('cursor', 'pointer')
      .on('click', (_, d) => onNodeClick?.(d));

    const label = svg
      .append('g')
      .selectAll('text')
      .data(simulationNodes)
      .join('text')
      .text((d) => d.label)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4)
      .attr('fill', '#334155');

    simulation.on('tick', () => {
  link
    .attr(
      'x1',
      (d) => ((d.source as SimulationNode).x ?? 0)
    )
    .attr(
      'y1',
      (d) => ((d.source as SimulationNode).y ?? 0)
    )
    .attr(
      'x2',
      (d) => ((d.target as SimulationNode).x ?? 0)
    )
    .attr(
      'y2',
      (d) => ((d.target as SimulationNode).y ?? 0)
    );

  node
    .attr('cx', (d) => d.x ?? 0)
    .attr('cy', (d) => d.y ?? 0);

  label
    .attr('x', (d) => d.x ?? 0)
    .attr('y', (d) => d.y ?? 0);
});

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, width, height, onNodeClick]);

  return (
    <div
      className={clsx(
        'overflow-hidden rounded-lg border border-gray-200 bg-white',
        className
      )}
    >
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="w-full"
        viewBox={`0 0 ${width} ${height}`}
      />
    </div>
  );
};

export default NetworkGraphView;