# RFM Insights - Analysis Module

import pandas as pd
import numpy as np
import json
import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# RFM Segmentation Class
class RFMAnalysis:
    def __init__(self, data, user_id_col, recency_col, frequency_col, monetary_col, segment_type):
        """
        Initialize RFM Analysis with the customer data and column mappings
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Customer transaction data
        user_id_col : str
            Column name for customer ID
        recency_col : str
            Column name for recency (date of last purchase/activity)
        frequency_col : str
            Column name for frequency (number of purchases/activities)
        monetary_col : str
            Column name for monetary value (total spent)
        segment_type : str
            Type of business segment (e.g., 'ecommerce', 'subscription')
        """
        self.data = data
        self.user_id_col = user_id_col
        self.recency_col = recency_col
        self.frequency_col = frequency_col
        self.monetary_col = monetary_col
        self.segment_type = segment_type
        self.rfm_data = None
        self.rfm_segments = None
        
    def preprocess_data(self):
        """
        Preprocess the data for RFM analysis
        """
        # Create a copy of the data
        df = self.data.copy()
        
        # Convert recency column to datetime if it's not already
        if df[self.recency_col].dtype != 'datetime64[ns]':
            df[self.recency_col] = pd.to_datetime(df[self.recency_col])
        
        # Convert frequency and monetary columns to numeric
        df[self.frequency_col] = pd.to_numeric(df[self.frequency_col], errors='coerce')
        df[self.monetary_col] = pd.to_numeric(df[self.monetary_col], errors='coerce')
        
        # Drop rows with missing values
        df = df.dropna(subset=[self.user_id_col, self.recency_col, self.frequency_col, self.monetary_col])
        
        # Calculate recency in days from today
        today = datetime.datetime.now().date()
        df['recency_days'] = (today - df[self.recency_col].dt.date).dt.days
        
        # Keep only necessary columns
        self.data = df[[self.user_id_col, 'recency_days', self.frequency_col, self.monetary_col]]
        
        return self.data
    
    def calculate_rfm_scores(self):
        """
        Calculate RFM scores using quartiles
        """
        # Preprocess data if not done already
        if 'recency_days' not in self.data.columns:
            self.preprocess_data()
        
        # Create a copy of the data
        rfm_data = self.data.copy()
        
        # Calculate quartiles for recency, frequency, and monetary value
        r_quartiles = pd.qcut(rfm_data['recency_days'], 4, labels=False, duplicates='drop')
        f_quartiles = pd.qcut(rfm_data[self.frequency_col], 4, labels=False, duplicates='drop')
        m_quartiles = pd.qcut(rfm_data[self.monetary_col], 4, labels=False, duplicates='drop')
        
        # Assign scores (1 is best for recency, 4 is best for frequency and monetary)
        rfm_data['r_score'] = 4 - r_quartiles  # Invert recency score (lower days = higher score)
        rfm_data['f_score'] = f_quartiles + 1
        rfm_data['m_score'] = m_quartiles + 1
        
        # Calculate RFM score
        rfm_data['rfm_score'] = rfm_data['r_score'] * 100 + rfm_data['f_score'] * 10 + rfm_data['m_score']
        
        self.rfm_data = rfm_data
        return self.rfm_data
    
    def segment_customers(self):
        """
        Segment customers based on RFM scores
        """
        # Calculate RFM scores if not done already
        if self.rfm_data is None:
            self.calculate_rfm_scores()
        
        # Create a copy of the RFM data
        rfm_segments = self.rfm_data.copy()
        
        # Define segmentation rules
        def segment_rule(row):
            r, f, m = row['r_score'], row['f_score'], row['m_score']
            
            # Champions: high recency, frequency, and monetary value
            if r >= 4 and f >= 4 and m >= 4:
                return "Campeões"
            
            # Loyal Customers: high frequency and monetary value
            elif (f >= 3 and m >= 3) and r >= 3:
                return "Clientes Fiéis"
            
            # Potential Loyalists: recent customers with average frequency
            elif r >= 4 and (f >= 2 and f < 4) and (m >= 2 and m < 4):
                return "Fiéis em Potencial"
            
            # New Customers: recent customers with low frequency
            elif r >= 4 and f <= 1:
                return "Novos Clientes"
            
            # Promising: recent customers with low frequency but high monetary value
            elif r >= 3 and f <= 2 and m >= 3:
                return "Clientes Promissores"
            
            # Customers Needing Attention: average recency and frequency
            elif (r >= 2 and r < 4) and (f >= 2 and f < 4) and (m >= 2 and m < 4):
                return "Clientes que Precisam de Atenção"
            
            # About to Sleep: low recency, average frequency and monetary value
            elif r <= 2 and (f >= 2 and f < 4) and (m >= 2 and m < 4):
                return "Clientes Quase Dormentes"
            
            # Can't Lose Them: low recency but high frequency and monetary value
            elif r <= 2 and f >= 3 and m >= 3:
                return "Clientes que Não Posso Perder"
            
            # At Risk: low recency and average frequency
            elif r <= 2 and (f >= 2 and f < 4):
                return "Clientes em Risco"
            
            # Hibernating: low recency, frequency, and monetary value
            elif r <= 1 and f <= 2 and m <= 2:
                return "Clientes Hibernando"
            
            # Lost: lowest recency and frequency
            elif r <= 1 and f <= 1:
                return "Clientes Perdidos"
            
            # Default
            else:
                return "Outros"
        
        # Apply segmentation rule
        rfm_segments['segment'] = rfm_segments.apply(segment_rule, axis=1)
        
        self.rfm_segments = rfm_segments
        return self.rfm_segments
    
    def get_segment_counts(self):
        """
        Get counts of customers in each segment
        """
        if self.rfm_segments is None:
            self.segment_customers()
        
        segment_counts = self.rfm_segments['segment'].value_counts().to_dict()
        return segment_counts
    
    def get_segment_stats(self):
        """
        Get statistics for each segment
        """
        if self.rfm_segments is None:
            self.segment_customers()
        
        segment_stats = {}
        for segment in self.rfm_segments['segment'].unique():
            segment_data = self.rfm_segments[self.rfm_segments['segment'] == segment]
            stats = {
                'count': len(segment_data),
                'avg_recency': segment_data['recency_days'].mean(),
                'avg_frequency': segment_data[self.frequency_col].mean(),
                'avg_monetary': segment_data[self.monetary_col].mean(),
                'total_monetary': segment_data[self.monetary_col].sum()
            }
            segment_stats[segment] = stats
        
        return segment_stats
    
    def get_treemap_data(self):
        """
        Get data for RFM treemap visualization
        """
        if self.rfm_segments is None:
            self.segment_customers()
        
        # Group by segment and calculate metrics
        treemap_data = self.rfm_segments.groupby('segment').agg({
            self.user_id_col: 'count',
            self.monetary_col: 'sum'
        }).reset_index()
        
        # Rename columns
        treemap_data.columns = ['segment', 'customer_count', 'total_value']
        
        # Calculate percentage of total
        total_customers = treemap_data['customer_count'].sum()
        total_value = treemap_data['total_value'].sum()
        
        treemap_data['customer_percentage'] = (treemap_data['customer_count'] / total_customers * 100).round(1)
        treemap_data['value_percentage'] = (treemap_data['total_value'] / total_value * 100).round(1)
        
        return treemap_data.to_dict('records')
    
    def get_polar_area_data(self):
        """
        Get data for polar area chart visualization
        """
        if self.rfm_segments is None:
            self.segment_customers()
        
        # Count customers in each segment
        segment_counts = self.rfm_segments['segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']
        
        # Calculate percentage
        total = segment_counts['count'].sum()
        segment_counts['percentage'] = (segment_counts['count'] / total * 100).round(1)
        
        return segment_counts.to_dict('records')

# Predictive Analytics Class
class PredictiveAnalytics:
    def __init__(self, rfm_data):
        """
        Initialize Predictive Analytics with RFM data
        
        Parameters:
        -----------
        rfm_data : pandas.DataFrame
            RFM data with customer segments
        """
        self.rfm_data = rfm_data
        self.churn_model = None
        self.upsell_model = None
        self.ltv_model = None
        self.features = None
        
    def prepare_features(self):
        """
        Prepare features for predictive models
        """
        # Create a copy of the RFM data
        df = self.rfm_data.copy()
        
        # Create features from RFM scores and other metrics
        features = df[['r_score', 'f_score', 'm_score', 'rfm_score', 'recency_days']]
        
        # Add segment as one-hot encoded features
        segment_dummies = pd.get_dummies(df['segment'], prefix='segment')
        features = pd.concat([features, segment_dummies], axis=1)
        
        self.features = features
        return features
    
    def predict_churn(self):
        """
        Predict customer churn using Random Forest
        """
        # Prepare features if not done already
        if self.features is None:
            self.prepare_features()
        
        # Create target variable (churn)
        # Customers with low recency and frequency scores are considered churned
        churn = (self.rfm_data['r_score'] <= 2) & (self.rfm_data['f_score'] <= 2)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, churn, test_size=0.3, random_state=42
        )
        
        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Evaluate model
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'auc': roc_auc_score(y_test, y_prob)
        }
        
        # Get feature importance
        feature_importance = dict(zip(self.features.columns, model.feature_importances_))
        
        # Predict churn probability for all customers
        self.rfm_data['churn_probability'] = model.predict_proba(self.features)[:, 1]
        
        # Store model
        self.churn_model = model
        
        return {
            'metrics': metrics,
            'feature_importance': feature_importance,
            'predictions': self.rfm_data[['churn_probability']].to_dict('records')
        }
    
    def predict_upsell_crosssell(self):
        """
        Identify upsell/cross-sell opportunities using K-Means clustering
        """
        # Prepare features if not done already
        if self.features is None:
            self.prepare_features()
        
        # Select relevant features for clustering
        cluster_features = self.features[['r_score', 'f_score', 'm_score']]
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(cluster_features)
        
        # Find optimal number of clusters using silhouette score
        silhouette_scores = []
        K = range(2, 8)
        for k in K:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(scaled_features)
            silhouette_scores.append(silhouette_score(scaled_features, kmeans.labels_))
        
        # Get optimal K
        optimal_k = K[np.argmax(silhouette_scores)]
        
        # Fit K-Means with optimal K
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        kmeans.fit(scaled_features)
        
        # Add cluster labels to RFM data
        self.rfm_data['cluster'] = kmeans.labels_
        
        # Analyze clusters
        cluster_analysis = {}
        for cluster in range(optimal_k):
            cluster_data = self.rfm_data[self.rfm_data['cluster'] == cluster]
            analysis = {
                'count': len(cluster_data),
                'avg_recency_score': cluster_data['r_score'].mean(),
                'avg_frequency_score': cluster_data['f_score'].mean(),
                'avg_monetary_score': cluster_data['m_score'].mean(),
                'segments': cluster_data['segment'].value_counts().to_dict()
            }
            cluster_analysis[f'cluster_{cluster}'] = analysis
        
        # Identify upsell/cross-sell opportunities
        # High monetary score but low frequency score indicates upsell potential
        # High frequency score but low monetary score indicates cross-sell potential
        self.rfm_data['upsell_potential'] = (self.rfm_data['m_score'] >= 3) & (self.rfm_data['f_score'] <= 2)
        self.rfm_data['crosssell_potential'] = (self.rfm_data['f_score'] >= 3) & (self.rfm_data['m_score'] <= 2)
        
        # Store model
        self.upsell_model = kmeans
        
        return {
            'optimal_clusters': optimal_k,
            'silhouette_scores': dict(zip(K, silhouette_scores)),
            'cluster_analysis': cluster_analysis,
            'upsell_opportunities': self.rfm_data[self.rfm_data['upsell_potential']].shape[0],
            'crosssell_opportunities': self.rfm_data[self.rfm_data['crosssell_potential']].shape[0]
        }
    
    def predict_ltv(self):
        """
        Predict customer lifetime value (LTV) using XGBoost
        """
        # Prepare features if not done already
        if self.features is None:
            self.prepare_features()
        
        # Create target variable (LTV)
        # For simplicity, we'll use monetary value as a proxy for LTV
        # In a real-world scenario, you would use historical data to calculate actual LTV
        monetary_col = [col for col in self.rfm_data.columns if col not in ['r_score', 'f_score', 'm_score', 'rfm_score', 'recency_days', 'segment', 'cluster', 'churn_probability', 'upsell_potential', 'crosssell_potential']][0]
        ltv = self.rfm_data[monetary_col]
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, ltv, test_size=0.3, random_state=42
        )
        
        # Train XGBoost model
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Evaluate model
        mse = np.mean((y_test - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_test - y_pred))
        r2 = 1 - (np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2
        }
        
        # Get feature importance
        feature_importance = dict(zip(self.features.columns, model.feature_importances_))
        
        # Predict LTV for all customers
        self.rfm_data['predicted_ltv'] = model.predict(self.features)
        
        # Calculate LTV segments
        ltv_quantiles = pd.qcut(self.rfm_data['predicted_ltv'], 4, labels=['Low', 'Medium', 'High', 'Very High'])
        self.rfm_data['ltv_segment'] = ltv_quantiles
        
        # Store model
        self.ltv_model = model
        
        return {
            'metrics': metrics,
            'feature_importance': feature_importance,
            'ltv_segments': self.rfm_data['ltv_segment'].value_counts().to_dict()
        }
    
    def get_predictive_insights(self):
        """
        Get combined insights from all predictive models
        """
        insights = {}
        
        # Run all predictive models if not done already
        if 'churn_probability' not in self.rfm_data.columns:
            self.predict_churn()
        
        if 'upsell_potential' not in self.rfm_data.columns:
            self.predict_upsell_crosssell()
        
        if 'predicted_ltv' not in self.rfm_data.columns:
            self.predict_ltv()
        
        # Get high-value customers at risk of churning
        high_value_at_risk = self.rfm_data[
            (self.rfm_data['ltv_segment'].isin(['High', 'Very High'])) & 
            (self.rfm_data['churn_probability'] > 0.5)
        ]
        
        # Get customers with high upsell potential and low churn risk
        upsell_targets = self.rfm_data[
            (self.rfm_data['upsell_potential'] == True) & 
            (self.rfm_data['churn_probability'] < 0.3)
        ]
        
        # Get customers with high cross-sell potential and low churn risk
        crosssell_targets = self.rfm_data[
            (self.rfm_data['crosssell_potential'] == True) & 
            (self.rfm_data['churn_probability'] < 0.3)
        ]
        
        # Get top segments by LTV
        segment_ltv = self.rfm_data.groupby('segment')['predicted_ltv'].mean().sort_values(ascending=False).to_dict()
        
        insights = {
            'high_value_at_risk_count': len(high_value_at_risk),
            'upsell_targets_count': len(upsell_targets),
            'crosssell_targets_count': len(crosssell_targets),
            'segment_ltv_ranking': segment_ltv,
            'retention_recommendations': [
                "Ofereça programas de fidelidade para clientes de alto valor em risco de abandono",
                "Implemente campanhas de reativação para clientes hibernando com alto LTV potencial",
                "Crie ofertas personalizadas para clientes que não podem ser perdidos"
            ],
            'upsell_recommendations': [
                "Ofereça produtos premium para clientes com alto potencial de upsell",
                "Crie pacotes especiais para clientes fiéis com baixo valor monetário",
                "Desenvolva programas de assinatura para aumentar o valor dos clientes frequentes"
            ],
            'crosssell_recommendations': [
                "Recomende produtos complementares para clientes com alto potencial de cross-sell",
                "Crie bundles de produtos para clientes com compras frequentes de baixo valor",
                "Ofereça descontos em categorias não exploradas para clientes fiéis"
            ]
        }
        
        return insights

# API Functions for Frontend Integration
def analyze_rfm_data(data, user_id_col, recency_col, frequency_col, monetary_col, segment_type):
    """
    Analyze RFM data and return results for frontend visualization
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Customer transaction data
    user_id_col : str
        Column name for customer ID
    recency_col : str
        Column name for recency (date of last purchase/activity)
    frequency_col : str
        Column name for frequency (number of purchases/activities)
    monetary_col : str
        Column name for monetary value (total spent)
    segment_type : str
        Type of business segment (e.g., 'ecommerce', 'subscription')
    
    Returns:
    --------
    dict
        Results of RFM analysis and predictive analytics
    """
    # Initialize RFM Analysis
    rfm = RFMAnalysis(data, user_id_col, recency_col, frequency_col, monetary_col, segment_type)
    
    # Perform RFM Analysis
    rfm_segments = rfm.segment_customers()
    segment_counts = rfm.get_segment_counts()
    segment_stats = rfm.get_segment_stats()
    treemap_data = rfm.get_treemap_data()
    polar_area_data = rfm.get_polar_area_data()
    
    # Initialize Predictive Analytics
    predictive = PredictiveAnalytics(rfm_segments)
    
    # Perform Predictive Analytics
    churn_results = predictive.predict_churn()
    upsell_results = predictive.predict_upsell_crosssell()
    ltv_results = predictive.predict_ltv()
    insights = predictive.get_predictive_insights()
    
    # Combine results
    results = {
        'rfm_analysis': {
            'segment_counts': segment_counts,
            'segment_stats': segment_stats,
            'treemap_data': treemap_data,
            'polar_area_data': polar_area_data
        },
        'predictive_analytics': {
            'churn': churn_results,
            'upsell_crosssell': upsell_results,
            'ltv': ltv_results,
            'insights': insights
        }
    }
    
    return results