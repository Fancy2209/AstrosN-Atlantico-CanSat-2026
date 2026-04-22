<script lang="ts">
	import { onMount } from 'svelte';
	import * as Cesium from 'cesium';
	import {
		MartiniTerrainProvider,
		PMTilesHeightmapResource,
		WorkerFarmTerrainDecoder,
	} from "@mhaberler/cesium-martini";
	import '../../node_modules/cesium/Build/Cesium/Widgets/widgets.css'

	(window as any).CESIUM_BASE_URL = './build';

	const terrariumWorker = new Worker(
	  new URL("./terrarium.worker.ts", import.meta.url),
	  { type: "module" },
	);

	// Mapterhorn Terrarium-encoded elevation tiles via PMTiles
	const terrainResource = new PMTilesHeightmapResource({
	  url: "/ponte_de_sor_terrain.pmtiles",
	  tileSize: 512,
	  maxZoom: 12,
	  skipZoomLevels(z: number) {
	    return z % 3 != 0
	  },
	});

	// Terrarium format uses a different encoding scheme to Mapbox Terrain-RGB
	// @ts-ignore
	const terrainDecoder = new WorkerFarmTerrainDecoder({
	  worker: terrariumWorker,
	});

	// Construct terrain provider with Mapterhorn PMTiles datasource and Terrarium RGB decoding
	// @ts-ignore
	const terrainProvider = new MartiniTerrainProvider({
	  resource: terrainResource,
	  decoder: terrainDecoder,
	});

	// VersaTiles: free, unauthenticated satellite imagery (Copernicus Sentinel-2)
	const imageryProvider = Cesium.ImageryLayer.fromProviderAsync(
		Cesium.TileMapServiceImageryProvider.fromUrl(
			Cesium.buildModuleUrl("Assets/Textures/NaturalEarthII")
		)
	)

	let extent = Cesium.Rectangle.fromDegrees(-8.34387,38.978216,-7.824361,39.384634);
	Cesium.Camera.DEFAULT_VIEW_RECTANGLE = extent;
	Cesium.Camera.DEFAULT_VIEW_FACTOR = 0;
    let viewer: Cesium.Viewer;
	onMount(async () => {
		viewer = new Cesium.Viewer('cesiumContainer', {
			baseLayer: imageryProvider,
			terrainProvider: terrainProvider,
			baseLayerPicker: false,
			geocoder: false
		});
		viewer.camera.flyTo
	});
	
</script>

<div id="cesiumContainer">
</div>

<style>
#cesiumContainer {
    width: 100%;
    height: 100%;
    margin: 0;  
    padding: 0;
    overflow: hidden;
}
</style>