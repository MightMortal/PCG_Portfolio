using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class TerrainMaps
{
    public float[,] map;
    public Texture2D diffuse;
}

[System.Serializable]
public struct TextureConfiguration { public float maxHeight; public Color color; }

public class TerrainUtils : MonoBehaviour
{

    // Mesh generator filter function parameters
    public float meshExponentFactor = 30.0f;
    public float meshFactor = 1.7f;
    public float meshExponentPower = 2.0f;

    // Lineary interpolation
    public static float lerp(float a, float b, float t)
    {
        return a + (b - a) * t;
    }

    // Quintic filter function
    public static float quintic(float t)
    {
        return t * t * t * (t * (t * 6 - 15) + 10);
    }

    // Cosine filter function
    public static float cosine(float t)
    {
        return (1 - Mathf.Cos(t * Mathf.PI)) / 2;
    }

    // Cubic filter function
    public static float cubic(float t)
    {
        return -2 * t * t * t + 3 * t * t;
    }

    // Mesh generation for given heighmap
    public void generateMesh(GameObject terrainObject, TerrainMaps terrainMap)
    {
        Mesh mesh = new Mesh();
        int dimension = terrainMap.map.GetLength(0);

        Vector3[] vertices = new Vector3[dimension * dimension]; // Vertices matrix
        Vector2[] uvs = new Vector2[dimension * dimension]; // UV texture coordiantes for each vertex
        List<int> indices = new List<int>(); // Indices of each edge
                                             // Generation of vertices matrix
        for (int x = 0; x < dimension; x++)
        {
            // Use filter function in order to generate more feasible terrain
            float h = meshExponentFactor * Mathf.Pow(meshFactor * terrainMap.map[x, 0], meshExponentPower);
            vertices[x] = new Vector3(x, h, 0);
            uvs[x] = new Vector2(x * 1.0f / dimension, 0 * 1.0f / dimension);
        }
        // Generation of edges
        for (int i = dimension; i < dimension * dimension; i++)
        {
            int x = i % dimension;
            int y = i / dimension;
            float h = meshExponentFactor * Mathf.Pow(meshFactor * terrainMap.map[x, y], meshExponentPower);
            vertices[i] = new Vector3(x, h, y);
            uvs[i] = new Vector2(x * 1.0f / dimension, y * 1.0f / dimension);
            if (x == 0)
            {
                indices.Add(i - dimension);
                indices.Add(i);
                indices.Add(i - dimension + 1);
            }
            else if (x == dimension - 1)
            {
                indices.Add(i - dimension);
                indices.Add(i - 1);
                indices.Add(i);
            }
            else
            {
                indices.Add(i - dimension);
                indices.Add(i - 1);
                indices.Add(i);
                indices.Add(i - dimension);
                indices.Add(i);
                indices.Add(i - dimension + 1);
            }
        }
        mesh.SetVertices(new List<Vector3>(vertices));
        mesh.SetIndices(indices.ToArray(), MeshTopology.Triangles, 0);
        mesh.SetUVs(0, new List<Vector2>(uvs));
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        MeshFilter meshFilter = terrainObject.GetComponent<MeshFilter>();
        meshFilter.mesh = mesh;
        ((MeshRenderer)(terrainObject.GetComponent<MeshRenderer>())).material.mainTexture = terrainMap.diffuse;
        ((MeshCollider)(terrainObject.GetComponent<MeshCollider>())).sharedMesh = mesh;
    }

    // Generate 2D grayscale texture for given heightmap
    public static Texture2D generate2DMap(TerrainMaps terrainMap)
    {
        Texture2D result = new Texture2D(terrainMap.map.GetLength(0), terrainMap.map.GetLength(0));
        for (int x = 0; x < result.width; x++)
        {
            for (int y = 0; y < result.height; y++)
            {
                float r = terrainMap.map[x, y];
                result.SetPixel(x, y, new Color(r, r, r));
            }
        }
        result.Apply();
        return result;
    }

    // Generate 2D vectors texture for given heightmap
    public static Texture2D generate2DVectorsMap(TerrainMaps terrainMap)
    {
        Texture2D result = new Texture2D(terrainMap.map.GetLength(0), terrainMap.map.GetLength(0));
        for (int x = 0; x < result.width; x++)
        {
            for (int y = 0; y < result.height; y++)
            {
                float r = terrainMap.map[x, y];
                result.SetPixel(x, y, new Color(r, x * 1.0f / result.width, y * 1.0f / result.width));
            }
        }
        result.Apply();
        return result;
    }

    // Get point color based on it's height
    public static Color getPointColor(float r, List<TextureConfiguration> textureConfigurations)
    {
        // 2.0f used as maximum available value. Acctually, noise maximum height is 1.0f
        Color result = Color.black; float minThreshold = 2.0f;
        // Search for minimal available texture color configuration
        for (int i = 0; i < textureConfigurations.Count; i++)
        {
            if (r < textureConfigurations[i].maxHeight && textureConfigurations[i].maxHeight < minThreshold)
            {
                result = textureConfigurations[i].color;
                minThreshold = textureConfigurations[i].maxHeight;
            }
        }
        return result;
    }
}
