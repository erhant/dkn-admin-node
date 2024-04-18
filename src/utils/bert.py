import random

import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel


class BertEmbedding:
    """

    BertEmbedding class to generate embeddings and calculate cosine similarity between vectors

    """

    def __init__(self, model_name='bert-base-uncased', random_seed=42):
        """
        Initialize the BertEmbedding class with the given model name and random seed

        :param model_name: Model name to use for embeddings, defaults to 'bert-base-uncased'
        :param random_seed: Random seed for reproducibility, defaults to 42
        """

        self.model_name = model_name
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)

        random.seed(random_seed)
        torch.manual_seed(random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(random_seed)

    def generate_embeddings(self, texts, add_special_tokens=True, cls_only=False, max_length=None):
        """
        Generate embeddings for the given texts

        :param texts: Texts to generate embeddings for, list of strings
        :param add_special_tokens: Should special tokens be added, defaults to True
        :param cls_only: Should only the CLS token be used, defaults to False
        :param max_length: Maximum length of the input, defaults to None
        :return: Embeddings for the given texts

        """
        encoding = self.tokenizer.batch_encode_plus(
            texts,
            padding='max_length' if max_length else True,
            max_length=max_length,
            truncation=True,
            return_tensors='pt',
            add_special_tokens=add_special_tokens
        )

        input_ids = encoding['input_ids']
        attention_mask = encoding['attention_mask']

        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            word_embeddings = outputs.last_hidden_state

        if cls_only:
            cls_embeddings = word_embeddings[:, 0, :]
            return cls_embeddings
        else:
            return word_embeddings

    @staticmethod
    def cosim(vec1, vec2):
        """
        Calculate the cosine similarity between two vectors

        :param vec1: Vector 1
        :param vec2: Vector 2
        :return: Cosine similarity between the two vectors
        """
        return cosine_similarity(vec1.numpy(), vec2.numpy())

    @staticmethod
    def maxsim(query_embeddings, doc_embeddings):
        """
        In this scoring function, Q represents the matrix of the query tokens, and
        D is the matrix of the passage tokens. The function computes the relevance by
        aligning each token from the query with the corresponding "most similar" token
        from the passage, and the overall relevance score is the sum of these individual
        token-level similarity score

        :param query_embeddings: Embedding for the query
        :param doc_embeddings: Embeddings for the documents
        :return: Maximum cosine similarity between the query and document embeddings
        """
        # Convert embeddings to numpy arrays outside the loop
        query_embeddings_np = query_embeddings.numpy()[0, :, :]  # Assuming the first query is the only one used
        doc_embeddings_np = doc_embeddings.numpy()

        # Compute all cosine similarities at once if memory allows
        similarity_scores = cosine_similarity(query_embeddings_np, doc_embeddings_np)

        # Compute the maximum similarity across the first dimension (across all docs for each query)
        max_similarities = np.max(similarity_scores, axis=1)

        # Calculate the sum of the maximum cosine similarities
        sum_max_similarities = max_similarities.sum()

        return sum_max_similarities
