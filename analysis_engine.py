
import base64
import boto3
from openai import OpenAI
from flask import Flask, jsonify, request




app = Flask(__name__)






# Initialize the S3 client

s3 = boto3.client('s3', aws_access_key_id= AWS_ID, aws_secret_access_key=AWS_KEY)
client = OpenAI(api_key= OpenAI_key)



# Function to fetch image from S3 and convert to base64 string
def fetch_image_from_s3(bucket_name, object_key):
    s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_data = s3_response['Body'].read()
    return base64.b64encode(image_data).decode('utf-8')





# Function to fetch all image paths from the folder in S3

def fetch_all_images_from_s3(bucket_name, folder_path):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(('.png', '.jpg', '.jpeg'))]



# Analyse a single chart

def analyze_stock_chart(base64_image_string, stock_name):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Analyze the stock chart image and provide the net return over the last 3 months."},
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze the chart for {stock_name}. How much net return did the stock give in the last 3 months?"},
                {"type": "image_url", "image_url": { "url": f"data:image/png;base64,{base64_image_string}"}}
            ]}
        ],
        temperature=0,
    )
    return response.choices[0].message.content


# Iterate over all charts and generate the top 3 performing stocks

def analyze_and_infer_top_stocks_combined(bucket_name, folder_path):
# Fetch all images from the S3 folder
    image_keys = fetch_all_images_from_s3(bucket_name, folder_path)
    
    stock_returns = []
    
    for image_key in image_keys:
        stock_name = image_key.split('/')[-1].split('.')[0]  # Assuming stock name is part of the image filename without extension
        base64_image_string = fetch_image_from_s3(bucket_name, image_key)
        net_return_sentence = analyze_stock_chart(base64_image_string, stock_name)
        
        stock_returns.append(f"Stock: {stock_name}, Return: {net_return_sentence}")
    
    stock_returns_str = "\n".join(stock_returns)
    
# Send the combined results for top 3 stock inference
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an analyst tasked with choosing the top 3 stocks based on net returns. Incase less than 3 stocks are provided, just give the return of those "},
            {"role": "user", "content": f"Here is the list of stocks and their net returns:\n{stock_returns_str}\nPlease identify the top 3 performing stocks."}
        ],
        temperature=0,
    )
    
    return response.choices[0].message.content


@app.route('/analyze_stocks', methods=['POST'])
def analyze_stocks():
    data = request.get_json()
    bucket_name = data.get("bucket_name")
    folder_path = data.get("folder_path")

    if not bucket_name or not folder_path:
        return jsonify({"error": "bucket_name and folder_path are required"}), 400

    top_stocks = analyze_and_infer_top_stocks_combined(bucket_name, folder_path)

    return jsonify({"top_stocks": top_stocks})





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
