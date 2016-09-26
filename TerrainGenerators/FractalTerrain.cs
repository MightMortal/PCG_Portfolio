using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class FractalTerrain : MonoBehaviour
{
    public int seed = 1319741; // Random generator seed
    public bool regenerateAllFlag; // Used to call generator from editor
    public bool regenerateMeshFlag; // Used to update mesh generator from editor
    public bool regenerateTextureFlag; // Used to update diffuse texture from editor
    public GameObject terrainObject; // Object, used as MeshRendrer
    public GameObject player; // Player, used to place player on the map after regeration
    public TerrainUtils terrainUtils; // Terrain utils, used to mesh generation and some math functions
    public List<TextureConfiguration> textureConfigurations; // Diffuse texture configuration
    public Texture2D mapImage; // Grayscale image of heighmap

    private TerrainMaps terrainMap; // Collection of heightmap and diffuse texture
    private int dimension = 255;

    // Use this for initialization
    void Start()
    {
        regenerateAllFlag = true;
    }

    // Update is called once per frame
    void Update()
    {
        if (regenerateAllFlag)
        {
            regenerateAllFlag = false;
            regenerateAll();
        }
        else if (regenerateMeshFlag)
        {
            regenerateMeshFlag = false;
            terrainUtils.generateMesh(terrainObject, terrainMap);
        }
        else if (regenerateTextureFlag)
        {
            regenerateTextureFlag = false;
            generateDifuseTexture(terrainMap);
            ((MeshRenderer)(terrainObject.GetComponent<MeshRenderer>())).material.mainTexture = terrainMap.diffuse;
        }
    }

    // Regenerate all elements, such as diffuse texture, heightmap and mesh
    private void regenerateAll()
    {
        int dimension = this.dimension;
        Random.InitState(seed);
        int arrSize = (dimension + 1) * (dimension + 1);
        List<float> amplitudes = new List<float>();
        terrainMap = new TerrainMaps();
        terrainMap.diffuse = new Texture2D(dimension, dimension);
        terrainMap.map = new float[dimension, dimension];
        terrainMap = generateTerrain(2, terrainMap);
        terrainUtils.generateMesh(terrainObject, terrainMap);
        ((MeshRenderer)(terrainObject.GetComponent<MeshRenderer>())).material.mainTexture = terrainMap.diffuse;
        player.transform.position = new Vector3(player.transform.position.x, 150, player.transform.position.z);
        mapImage = TerrainUtils.generate2DMap(terrainMap);
    }

    // Diffure (color) texture regenration without mesh and heightmap regeneration
    private void generateDifuseTexture(TerrainMaps maps)
    {
        for (int x = 0; x < maps.diffuse.width; x++)
        {
            for (int y = 0; y < maps.diffuse.height; y++)
            {
                maps.diffuse.SetPixel(x, y, TerrainUtils.getPointColor(maps.map[x, y], textureConfigurations));
            }
        }
        maps.diffuse.Apply();
    }

    // Main fractal-based generation method. This is the recursion method
    private TerrainMaps generateTerrain(int division, TerrainMaps maps)
    {
        int step = dimension / division;
        if (step < 8) // Terminal step, if step less than 8 points (meters)
        {
            // Search for maximum and minimal height
            float maxHeight = 0.0f;
            float minHeight = 12311230.0f;
            for (int x = 0; x < dimension; x++)
                for (int y = 0; y < dimension; y++)
                {
                    if (terrainMap.map[x, y] > maxHeight)
                        maxHeight = terrainMap.map[x, y];
                    if (terrainMap.map[x, y] < minHeight)
                        minHeight = terrainMap.map[x, y];
                }

            // Normalize and apply non-linear filter to the heightmap
            for (int x = 0; x < dimension; x++)
                for (int y = 0; y < dimension; y++)
                {
                    float r = TerrainUtils.quintic((terrainMap.map[x, y] - minHeight) / (maxHeight - minHeight));
                    terrainMap.map[x, y] = r;
                }

            generateDifuseTexture(maps);
            return maps;
        }

        // Shift keypoints verticaly
        for (int x = 0; x * step < dimension; x++)
            for (int y = 0; y * step < dimension; y++)
            {
                terrainMap.map[x * step, y * step] = Random.value + terrainMap.map[x * step, y * step] * 3;
            }

        // Linear interpolation of the values between keypoints
        for (int x = 0; x < dimension; x++)
        {
            for (int y = 0; y < dimension; y++)
            {
                if (x % step == 0 && y % step == 0) // Skip keypoints
                    continue;
                // Calculate position of neares keypoints and current position between them
                int qx = x / step, qy = y / step;
                int qxOffset = x % step, qyOffset = y % step;
                int xOffset = 1, yOffset = 1;
                if ((qx + xOffset) * step >= dimension)
                    xOffset = 0;
                if ((qy + yOffset) * step >= dimension)
                    yOffset = 0;
                // Get keypoints heights
                float tl = terrainMap.map[qx * step, qy * step];
                float tr = terrainMap.map[(qx + xOffset) * step, qy * step];
                float bl = terrainMap.map[qx * step, (qy + yOffset) * step];
                float br = terrainMap.map[(qx + xOffset) * step, (qy + yOffset) * step];
                // Linear interpolation
                float tx = qxOffset * 1.0f / step, ty = qyOffset * 1.0f / step;
                float t = TerrainUtils.lerp(tl, tr, tx);
                float b = TerrainUtils.lerp(bl, br, tx);
                float r = TerrainUtils.lerp(t, b, ty);
                terrainMap.map[x, y] = r;
            }
        }
        // Recursive call with smaller size of quad. Equivalent to mesh edge division
        return generateTerrain(division * 2, maps);
    }

}
