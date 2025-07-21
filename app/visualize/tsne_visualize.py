#pip install scikit-learn matplotlib weaviate-client
#python app/visualize/tsne_visualize.py
# not working as of now - need to fix (too much time consuming)

import weaviate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plot

# Limit how many to plot
MAX_POINTS = 300  # Optional: limit for performance

def fetch_vectors_from_weaviate():
    client = weaviate.Client("http://localhost:8080")

    if not client.is_ready():
        raise Exception("Weaviate server not ready or unreachable at :8080")

    print("✅ Connected to Weaviate")

    query = (
        client.query
        .get("PageChunk", ["chunk_id", "url"])
        .with_additional(["vector"])
        .with_limit(MAX_POINTS)
    )
    result = query.do()

    chunks = result["data"]["Get"]["PageChunk"]

    vectors = []
    labels = []
    urls = []

    for chunk in chunks:
        vector = chunk["_additional"]["vector"]
        vectors.append(vector)
        labels.append(chunk["chunk_id"])
        urls.append(chunk["url"])

    print(f"✅ Fetched {len(vectors)} vectors.")
    return np.array(vectors), labels, urls


def plot_tsne_2d(vectors, labels):
    print("📉 Running t-SNE for 2D...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, init="pca", n_iter=1000)
    X_2d = tsne.fit_transform(vectors)

    plt.figure(figsize=(10, 8))
    plt.scatter(X_2d[:, 0], X_2d[:, 1], s=10, alpha=0.7)

    for i, label in enumerate(labels):
        if i % 20 == 0:  # Label every 20th for clarity
            plt.annotate(label[:12], (X_2d[i, 0], X_2d[i, 1]), fontsize=8, alpha=0.6)

    plt.title("2D t-SNE of PageChunk Embeddings")
    plt.xlabel("t-SNE Dim 1")
    plt.ylabel("t-SNE Dim 2")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_tsne_3d(vectors, labels):
    print("📉 Running t-SNE for 3D...")
    tsne = TSNE(n_components=3, random_state=42, perplexity=30, init="pca", n_iter=1000)
    X_3d = tsne.fit_transform(vectors)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(X_3d[:, 0], X_3d[:, 1], X_3d[:, 2], s=10, alpha=0.7)

    for i, label in enumerate(labels):
        if i % 20 == 0:  # Label every 20th
            ax.text(X_3d[i, 0], X_3d[i, 1], X_3d[i, 2], label[:8], size=7)

    ax.set_title("3D t-SNE of PageChunk Embeddings")
    plt.tight_layout()
    plt.show()


def main():
    vectors, labels, urls = fetch_vectors_from_weaviate()
    plot_tsne_2d(vectors, labels)
    plot_tsne_3d(vectors, labels)


if __name__ == "__main__":
    main()

