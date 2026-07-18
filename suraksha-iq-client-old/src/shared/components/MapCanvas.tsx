import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import clsx from 'clsx';

export interface MapMarker {
  id: string;
  latitude: number;
  longitude: number;
  intensity?: number;
  label?: string;
}

export interface ChoroplethRegion {
  id: string;
  geojson: GeoJSON.Feature;
  value: number;
}

interface MapCanvasProps {
  center?: [number, number];
  zoom?: number;
  markers?: MapMarker[];
  choropleth?: ChoroplethRegion[];
  className?: string;
  onMarkerClick?: (marker: MapMarker) => void;
}

const MapCanvas: React.FC<MapCanvasProps> = ({
  center = [77.5946, 12.9716],
  zoom = 7,
  markers = [],
  choropleth = [],
  className,
  onMarkerClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center,
      zoom,
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    mapRef.current = map;

    return () => {
      markersRef.current.forEach((m) => m.remove());
      map.remove();
      mapRef.current = null;
    };
  }, [center, zoom]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = markers.map((marker) => {
      const el = document.createElement('div');
      el.className = clsx(
        'flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border-2 border-white text-xs font-bold text-white shadow',
        marker.intensity && marker.intensity > 70
          ? 'bg-alert-red'
          : marker.intensity && marker.intensity > 40
            ? 'bg-amber-analytics'
            : 'bg-viz-blue'
      );
      el.textContent = marker.label?.charAt(0) ?? '•';
      el.title = marker.label ?? marker.id;
      el.addEventListener('click', () => onMarkerClick?.(marker));

      const mapMarker = new maplibregl.Marker({ element: el })
        .setLngLat([marker.longitude, marker.latitude])
        .addTo(map);
      return mapMarker;
    });
  }, [markers, onMarkerClick]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || choropleth.length === 0) return;

    const sourceId = 'choropleth-source';
    const layerId = 'choropleth-layer';

    const addLayer = () => {
      if (map.getSource(sourceId)) {
        (map.getSource(sourceId) as maplibregl.GeoJSONSource).setData({
          type: 'FeatureCollection',
          features: choropleth.map((r) => r.geojson),
        });
        return;
      }

      map.addSource(sourceId, {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: choropleth.map((r) => r.geojson),
        },
      });

      map.addLayer({
        id: layerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'value'],
            0,
            '#dbeafe',
            50,
            '#3b82f6',
            100,
            '#9333ea',
          ],
          'fill-opacity': 0.6,
        },
      });
    };

    if (map.isStyleLoaded()) addLayer();
    else map.on('load', addLayer);
  }, [choropleth]);

  return (
    <div
      ref={containerRef}
      className={clsx('h-[400px] w-full overflow-hidden rounded-lg border border-gray-200', className)}
    />
  );
};

export default MapCanvas;
