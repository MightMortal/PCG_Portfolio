using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class PerlinNoiseTerrain : MonoBehaviour
{
    [System.Serializable]
    public struct NoiseConfiguration { public int amplitude; public float frequency; }

    public int seed = 1319741; // Random generator seed
    public bool regenerateAllFlag; // Used to call generator from editor
    public bool regenerateMeshFlag; // Used to update mesh generator from editor
    public bool regenerateTextureFlag; // Used to update diffuse texture from editor
    public GameObject terrainObject; // Object, used as MeshRendrer
    public GameObject player; // Player, used to place player on the map after regeration
    public TerrainUtils terrainUtils; // Terrain utils, used to mesh generation and some math functions
    public List<NoiseConfiguration> noisesConfigurations; // Noise configuration
    public List<TextureConfiguration> textureConfigurations; // Diffuse texture configuration
    public Texture2D mapImage; // Grayscale image of heighmap

    private int dimension = 255; // Size of one side of the map
    private int[] permutationTable; // Permutation table used for determined pseudorandom values generation
    private List<float[,]> noises = new List<float[,]>(); // List of generated noises, used during textures/mesh generation
    private TerrainMaps terrainMap; // Collection of heightmap and diffuse texture

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
            List<float> amplitudes = new List<float>();
            for (int i = 0; i < noisesConfigurations.Count; i++)
            {
                amplitudes.Add(noisesConfigurations[i].amplitude);
            }
            terrainMap.diffuse = generateDifuseTexture(noises, amplitudes);
            ((MeshRenderer)(terrainObject.GetComponent<MeshRenderer>())).material.mainTexture = terrainMap.diffuse;
        }
    }

    // Regenerate all elements, such as diffuse texture, heightmap and mesh
    private void regenerateAll()
    {
        Random.InitState(seed);
        int arrSize = (dimension + 1) * (dimension + 1);
        permutationTable = new int[arrSize];
        for (int i = 0; i < arrSize; i++)
        {
            permutationTable[i] = ((int)(Random.value * Mathf.Pow(2, 30)));
        }
        List<float> amplitudes = new List<float>();
        noises = new List<float[,]>();
        for (int i = 0; i < noisesConfigurations.Count; i++)
        {
            noises.Add(generateNoise(noisesConfigurations[i].frequency));
            amplitudes.Add(noisesConfigurations[i].amplitude);
        }
        terrainMap = generateMapTexture(noises, amplitudes);
        terrainUtils.generateMesh(terrainObject, terrainMap);
        player.transform.position = new Vector3(player.transform.position.x, 150, player.transform.position.z);
        mapImage = TerrainUtils.generate2DMap(terrainMap);
    }

    // Regeneration of both, diffuse texture and heightmap
    private TerrainMaps generateMapTexture(List<float[,]> noises, List<float> amplitudes)
    {
        float[,] map = new float[dimension, dimension];
        Texture2D tex = new Texture2D(dimension, dimension);
        float totalAmplitude = 0.0f;
        for (int i = 0; i < noises.Count; i++)
        {
            totalAmplitude += amplitudes[i];
        }
        for (int x = 0; x < dimension; x++)
        {
            for (int y = 0; y < dimension; y++)
            {
                float r = 0.0f;
                for (int i = 0; i < noises.Count; i++)
                {
                    r += noises[i][x, y] * amplitudes[i];
                }
                r = r / totalAmplitude; // Normalize sum of noises
                r = TerrainUtils.quintic(TerrainUtils.quintic(r)); // Apply non-linear filter
                map[x, y] = r;
                tex.SetPixel(x, y, TerrainUtils.getPointColor(r, textureConfigurations));
            }
        }
        tex.Apply();
        TerrainMaps result = new TerrainMaps();
        result.map = map;
        result.diffuse = tex;
        return result;
    }

    // Diffure (color) texture regenration without mesh and heightmap regeneration
    private Texture2D generateDifuseTexture(List<float[,]> noises, List<float> amplitudes)
    {
        Texture2D tex = new Texture2D(dimension, dimension);
        float totalAmplitude = 0.0f;
        for (int i = 0; i < noises.Count; i++)
        {
            totalAmplitude += amplitudes[i];
        }
        for (int x = 0; x < dimension; x++)
        {
            for (int y = 0; y < dimension; y++)
            {
                float r = 0.0f;
                for (int i = 0; i < noises.Count; i++)
                {
                    r += noises[i][x, y] * amplitudes[i];
                }
                r = r / totalAmplitude; // Normalize sum of noises
                r = TerrainUtils.quintic(TerrainUtils.quintic(r)); // Apply non-linear filter
                tex.SetPixel(x, y, TerrainUtils.getPointColor(r, textureConfigurations));
            }
        }
        tex.Apply();
        return tex;
    }

    // Functon for generation of noise with given frequency multiplier
    float[,] generateNoise(float mult)
    {
        float[,] noise = new float[dimension, dimension];
        for (int x = 0; x < dimension; x++)
            for (int y = 0; y < dimension; y++)
            {
                float r = PerlinNoise(new Vector2(x * mult / dimension, y * mult / dimension));
                r = (r + 1.0f) / 2.0f;
                noise[x, y] = r;
            }

        return noise;
    }

    // Get pseudorandom gradient for each keypoint of the noise
    Vector2 getRandomGradient(int x, int y)
    {
        Random.InitState(permutationTable[x * dimension + y]);
        Vector2 result = new Vector2((Random.value - 0.5f) * 2.0f, (Random.value - 0.5f) * 2.0f);
        return result.normalized;
    }

    float PerlinNoise(Vector2 vec)
    {
        // Calculate position of nearest keypoint in up/left direction and distance in quad
        int left = Mathf.FloorToInt(vec.x), top = Mathf.FloorToInt(vec.y);
        Vector2 positionInQuad = new Vector2(vec.x - left, vec.y - top);
        // Get pseudorandom gradients for near keypoints
        Vector2 gradientTL = getRandomGradient(left, top);
        Vector2 gradientTR = getRandomGradient(left + 1, top);
        Vector2 gradientBL = getRandomGradient(left, top + 1);
        Vector2 gradientBR = getRandomGradient(left + 1, top + 1);
        // Calculate distance vectors to each of near keypoints
        Vector2 distanceToTL = new Vector2(positionInQuad.x, positionInQuad.y);
        Vector2 distanceToTR = new Vector2(positionInQuad.x - 1, positionInQuad.y);
        Vector2 distanceToBL = new Vector2(positionInQuad.x, positionInQuad.y - 1);
        Vector2 distanceToBR = new Vector2(positionInQuad.x - 1, positionInQuad.y - 1);
        // Calculate distance to each keypoint's gradient vector
        float tx1 = Vector2.Dot(distanceToTL, gradientTL);
        float tx2 = Vector2.Dot(distanceToTR, gradientTR);
        float bx1 = Vector2.Dot(distanceToBL, gradientBL);
        float bx2 = Vector2.Dot(distanceToBR, gradientBR);
        // Make interpolation non-linear
        float qx = TerrainUtils.quintic(positionInQuad.x), qy = TerrainUtils.quintic(positionInQuad.y);
        // Interpolate value
        float tx = TerrainUtils.lerp(tx1, tx2, qx), bx = TerrainUtils.lerp(bx1, bx2, qx);
        float tb = TerrainUtils.lerp(tx, bx, qy);
        return tb;
    }
}
