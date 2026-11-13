import argparse
from io import BytesIO

import boto3
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image, ImageOps


def detect_labels(bucket, key, region, output_path):
    session = boto3.Session(region_name=region)
    rekognition = session.client("rekognition")
    s3 = session.client("s3")

    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
        MinConfidence=70,
    )

    image_bytes = s3.get_object(Bucket=bucket, Key=key)["Body"].read()

    with Image.open(BytesIO(image_bytes)) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image)
    ax.axis("off")

    for label in response["Labels"]:
        print(f'{label["Name"]}: {label["Confidence"]:.1f}%')

        for instance in label.get("Instances", []):
            box = instance["BoundingBox"]

            left = box["Left"] * image.width
            top = box["Top"] * image.height
            width = box["Width"] * image.width
            height = box["Height"] * image.height

            ax.add_patch(
                Rectangle(
                    (left, top),
                    width,
                    height,
                    fill=False,
                    edgecolor="red",
                    linewidth=2,
                )
            )

            ax.text(
                left,
                max(0, top - 4),
                f'{label["Name"]} ({instance["Confidence"]:.1f}%)',
                color="red",
                fontsize=9,
                bbox={"facecolor": "white", "alpha": 0.8},
            )

    fig.savefig(output_path, bbox_inches="tight", dpi=160)
    plt.close(fig)

    print(f"\nLabels detected: {len(response['Labels'])}")
    print(f"Annotated image saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect labels in an S3 image using Amazon Rekognition."
    )
    parser.add_argument("bucket", help="S3 bucket name")
    parser.add_argument("key", help="S3 object key")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--output", default="labeled-image.png")
    args = parser.parse_args()

    detect_labels(args.bucket, args.key, args.region, args.output)


if __name__ == "__main__":
    main() 
