import re
import matplotlib.pyplot as plt
import io
import base64

def extract_number(file_name):
    '''Used to sort pre-trained models, otherwise model2 > model16'''
    match = re.search(r'\d+', file_name)  # Find the first number in the string
    return int(match.group()) if match else 0

def plot_train(scores, mean_scores):
    '''The image is formated to send to html frontend'''
    img = io.BytesIO()
    plt.figure(figsize=(5, 5))
    plt.clf()
    plt.title('Training reinforcement learning model...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    
    # Encode the image as base64
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url