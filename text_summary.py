
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt_tab')
def get_frequency_table(text_string: str) -> dict:
    
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text_string)
    ps = PorterStemmer()
    
    freqTable = dict()
    for word in words:
        word = word.lower()
        # Filter out punctuation and non-alphanumeric tokens
        if not word.isalnum():
            continue
        # Skip stopwords
        if word in stop_words:
            continue
        if word.isdigit():
            continue
        # Stem the word
        stemmed_word = ps.stem(word)
        freqTable[stemmed_word] = freqTable.get(stemmed_word, 0) + 1
        
    return freqTable

def sentence_score_table(sentences: list, freqTable: dict) -> dict:
    
    stop_words = set(stopwords.words("english"))
    ps = PorterStemmer()
    sentenceValue = dict()
    
    for sentence in sentences:
        # Tokenize the sentence and convert to lowercase
        words = word_tokenize(sentence.lower())
        # Filter out punctuation, stopwords, and digits, and apply stemming
        filtered_words = [ps.stem(word) for word in words 
                          if word.isalnum() and word not in stop_words and not word.isdigit()]
        
        if len(filtered_words) == 0:
            continue
        
        # Calculate sentence score
        sentence_score = sum(freqTable.get(word, 0) for word in filtered_words)
        sentenceValue[sentence] = sentence_score / len(filtered_words)
    
    return sentenceValue
def avg_sentence_score(sentenceValue: dict) -> float:
   
    if len(sentenceValue) == 0:
        return 0
    total_score = sum(sentenceValue.values())
    average = total_score / len(sentenceValue)
    return average
def generate_summary(sentences: list, sentenceValue: dict, threshold: float, max_sentences: int = 8) -> list:
   
    sentence_count = 0
    summary_sentences = []
    seen = set()  # to track normalized sentences for duplicate detection
    
    for sentence in sentences:
        if sentence in sentenceValue and sentenceValue[sentence] >= threshold:
            normalized_sentence = sentence.strip().lower()
            if normalized_sentence not in seen:
                summary_sentences.append(sentence)
                seen.add(normalized_sentence)
                sentence_count += 1
            if sentence_count >= max_sentences:
                break
            
    return summary_sentences

def group_sentences_by_sentiment(sentences: list):
    
    sia = SentimentIntensityAnalyzer()
    pos_sentences = []
    neg_sentences = []
    neu_sentences = []
    for sentence in sentences:
        scores = sia.polarity_scores(sentence)
        if scores['compound'] > 0.1:
            pos_sentences.append(sentence)
        elif scores['compound'] < -0.1:
            neg_sentences.append(sentence)
        else:
            neu_sentences.append(sentence)
    return pos_sentences, neg_sentences, neu_sentences


from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment import SentimentIntensityAnalyzer

def overall_sentiment(sentences) -> str:
    sia = SentimentIntensityAnalyzer()

    # Ensure input is a string or list of sentences
    if isinstance(sentences, float) or sentences is None:
        return "No sentiment information available."
    
    if isinstance(sentences, str):
        sentences = [sentences]
    
    # Handle empty input
    if not sentences:
        return "No sentiment information available."
    
    # Calculate compound scores
    compound_scores = [sia.polarity_scores(sentence)['compound'] for sentence in sentences if sentence.strip()]
    
    if not compound_scores:
        return "No sentiment information available."
    
    # print(f"{compound_scores} -------------------- Compound Scores")

    avg_score = sum(compound_scores) / len(compound_scores)
    # print(f"{avg_score} -------------------- Avg Score")

    # Determine overall sentiment
    if avg_score > 0.1:
        return "positive"
    elif avg_score < -0.1:
        return "negative"
    else:
        return "mixed"


def fix_letter_spacing(text: str) -> str:
   
    # Check if there are any occurrences of two or more consecutive spaces.
    if not re.search(r'\s{2,}', text):
        return text  # No extra spacing detected; return the text as-is.
    
    # Otherwise, fix the spacing.
    word_groups = re.split(r'\s{2,}', text)
    fixed_groups = []
    for group in word_groups:
        fixed_group = group.replace(" ", "")
        fixed_groups.append(fixed_group)
    return " ".join(fixed_groups)

def run_summarization(text: str) -> str:
  
    text = re.sub(r'\d+\.', '', text)
    # Remove non-ASCII characters (e.g., emojis)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    freq_table = get_frequency_table(text)
    sentences = sent_tokenize(text)
    sentence_scores = sentence_score_table(sentences, freq_table)
    threshold = avg_sentence_score(sentence_scores)
    # summary = _generate_summary(sentences, sentence_scores, threshold)
    summary_sentences = generate_summary(sentences, sentence_scores, threshold)
    # print(summary_sentences,"summary summary_sentences")

    # Group the summary sentences by sentiment
    pos_sentences, neg_sentences, neu_sentences = group_sentences_by_sentiment(summary_sentences)
    # print(pos_sentences,neg_sentences,neu_sentences,"summary parts")

    conclusion = overall_sentiment(summary_sentences)
    
    # Build the final summary by grouping similar sentiments together
    final_summary_parts = []
    if pos_sentences:
        final_summary_parts.append("Positive aspects: " + " ".join(pos_sentences))
    if neg_sentences:
        final_summary_parts.append("Negative aspects: " + " ".join(neg_sentences))
    if neu_sentences:
        final_summary_parts.append("Neutral observations: " + " ".join(neu_sentences))
    # Append the concluding sentence
    # final_summary_parts.append(conclusion)
    
    final_summary = " ".join(final_summary_parts)

    # return final_summary,conclusion
    return final_summary, conclusion, pos_sentences, neg_sentences, neu_sentences
