"""Content, cluster and hybrid ranking. Scores are not probabilities."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics.pairwise import linear_kernel

class Recommender:
    def __init__(self,books):
        self.books=books.reset_index(drop=True)
        text=self.books.title+' '+self.books.author+' '+self.books.genres.replace('Unknown','')+' '+self.books.description
        self.vectorizer=TfidfVectorizer(stop_words='english',max_features=20000,ngram_range=(1,2),sublinear_tf=True)
        self.matrix=self.vectorizer.fit_transform(text)
        self.clusters=MiniBatchKMeans(n_clusters=min(20,len(books)),random_state=42,n_init=3,batch_size=512).fit_predict(self.matrix)

    def recommend(self,book_id=None,text='',method='Content',limit=5,eligible=None):
        vector=self.matrix[book_id] if book_id is not None else self.vectorizer.transform([text])
        if not vector.nnz:
            return self.books.iloc[:0].assign(similarity=[],score=[])
        similarity=linear_kernel(vector,self.matrix).ravel()
        score=similarity.copy()
        mask=similarity>0
        if method=='Cluster':
            cluster=self.clusters[book_id] if book_id is not None else self.clusters[int(similarity.argmax())]
            mask &= self.clusters==cluster
        if method=='Hybrid':
            rating=self.books.rating.fillna(0).to_numpy()/5
            reviews=np.log1p(self.books.reviews.fillna(0).to_numpy())
            popularity=reviews/max(1,reviews.max())
            score=.8*similarity+.15*rating+.05*popularity
        if book_id is not None: mask[book_id]=False
        if eligible is not None: mask &= np.isin(np.arange(len(self.books)),eligible)
        indices=np.where(mask)[0]
        indices=indices[np.argsort(-score[indices],kind='stable')][:limit]
        result=self.books.iloc[indices].copy()
        result['similarity']=similarity[indices]; result['score']=score[indices]
        return result
