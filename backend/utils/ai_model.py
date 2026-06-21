import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import joblib
import json
import os
from flask import current_app

class CaseRecommender:
    def __init__(self, model_path=None):
        self.vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        self.scaler = StandardScaler()
        self.model_path = model_path or current_app.config.get('AI_MODEL_PATH', 'models/recommender_model.pkl')
        self.similarity_threshold = current_app.config.get('SIMILARITY_THRESHOLD', 0.3)
        
    def extract_features(self, case_data):
        """Extract and normalize features from case data"""
        features = {}
        
        # Text features - combine relevant fields
        text_fields = [
            ' '.join(case_data.get('symptoms', [])),
            case_data.get('diagnosis', ''),
            case_data.get('medical_history', ''),
            case_data.get('category', '')
        ]
        features['text'] = ' '.join(filter(None, text_fields))
        
        # Numerical features
        features['age'] = float(case_data.get('patient_age', 0))
        features['symptom_count'] = len(case_data.get('symptoms', []))
        
        # Categorical features encoding
        gender = case_data.get('patient_gender', '')
        features['is_male'] = 1.0 if gender == 'male' else 0.0
        features['is_female'] = 1.0 if gender == 'female' else 0.0
        
        severity = case_data.get('severity', '')
        features['severity_mild'] = 1.0 if severity == 'mild' else 0.0
        features['severity_moderate'] = 1.0 if severity == 'moderate' else 0.0
        features['severity_severe'] = 1.0 if severity == 'severe' else 0.0
        features['severity_critical'] = 1.0 if severity == 'critical' else 0.0
        
        # Lab results complexity (simplified)
        lab_results = case_data.get('lab_results', {})
        features['has_abnormal_labs'] = 1.0 if lab_results and len(lab_results) > 0 else 0.0
        
        return features
    
    def prepare_training_data(self, cases):
        """Prepare training data from cases"""
        features_list = []
        
        for case in cases:
            features = self.extract_features(case)
            features_list.append(features)
        
        # Convert to DataFrame
        df = pd.DataFrame(features_list)
        
        # Separate text and numerical features
        text_features = df['text'].fillna('')
        numerical_features = df.drop('text', axis=1).fillna(0)
        
        return text_features, numerical_features
    
    def train(self, cases):
        """Train the recommendation model"""
        if not cases:
            raise ValueError("No cases provided for training")
        
        text_features, numerical_features = self.prepare_training_data(cases)
        
        # Fit vectorizer on text features
        self.vectorizer.fit(text_features)
        
        # Fit scaler on numerical features
        if not numerical_features.empty:
            self.scaler.fit(numerical_features)
        
        # Save the trained model
        self.save_model()
        
        return True
    
    def find_similar_cases(self, new_case, existing_cases, top_n=5, min_similarity=0.0):
        """Find similar cases with similarity score above threshold"""
        if not existing_cases:
            return []
        
        # Prepare features for all cases
        all_cases = [new_case] + existing_cases
        text_features, numerical_features = self.prepare_training_data(all_cases)
        
        # Transform text features
        text_vectors = self.vectorizer.transform(text_features)
        
        # Transform numerical features if scaler was trained
        if hasattr(self.scaler, 'mean_') and numerical_features is not None:
            numerical_vectors = self.scaler.transform(numerical_features)
            # Combine text and numerical features
            from scipy.sparse import hstack
            feature_vectors = hstack([text_vectors, numerical_vectors])
        else:
            feature_vectors = text_vectors
        
        # Calculate similarity between new case and all existing cases
        new_case_vector = feature_vectors[0:1]
        existing_vectors = feature_vectors[1:]
        
        similarities = cosine_similarity(new_case_vector, existing_vectors).flatten()
        
        # Filter by minimum similarity threshold
        filtered_indices = np.where(similarities >= min_similarity)[0]
        
        if len(filtered_indices) == 0:
            # Return most similar even if below threshold
            filtered_indices = similarities.argsort()[-top_n:][::-1]
        else:
            # Get top N from filtered indices
            filtered_similarities = similarities[filtered_indices]
            top_filtered_indices = filtered_similarities.argsort()[-top_n:][::-1]
            filtered_indices = filtered_indices[top_filtered_indices]
        
        # Prepare results
        results = []
        for idx in filtered_indices:
            if idx < len(existing_cases):
                similarity_score = float(similarities[idx])
                if similarity_score >= self.similarity_threshold:
                    results.append({
                        'case': existing_cases[idx],
                        'similarity': similarity_score
                    })
        
        return results
    
    def generate_treatment_recommendations(self, similar_cases_with_scores):
        """Generate treatment recommendations with confidence scores"""
        if not similar_cases_with_scores:
            return []
        
        treatment_stats = {}
        
        for item in similar_cases_with_scores:
            case = item['case']
            similarity = item['similarity']
            
            # Get treatments from case
            treatments = case.get('treatments', [])
            
            for treatment in treatments:
                treatment_type = treatment.get('treatment_type')
                effectiveness = treatment.get('effectiveness', 'fair')
                
                if not treatment_type:
                    continue
                
                if treatment_type not in treatment_stats:
                    treatment_stats[treatment_type] = {
                        'count': 0,
                        'total_similarity': 0.0,
                        'effectiveness_scores': [],
                        'treatments': []  # Store individual treatment details
                    }
                
                # Map effectiveness to numerical score
                effectiveness_map = {
                    'excellent': 1.0,
                    'good': 0.75,
                    'fair': 0.5,
                    'poor': 0.25
                }
                
                treatment_stats[treatment_type]['count'] += 1
                treatment_stats[treatment_type]['total_similarity'] += similarity
                treatment_stats[treatment_type]['effectiveness_scores'].append(
                    effectiveness_map.get(effectiveness, 0.5)
                )
                
                # Store treatment details (for later reference)
                treatment_stats[treatment_type]['treatments'].append({
                    'description': treatment.get('description'),
                    'medication': treatment.get('medication'),
                    'dosage': treatment.get('dosage'),
                    'duration': treatment.get('duration'),
                    'effectiveness': effectiveness,
                    'case_similarity': similarity
                })
        
        # Calculate recommendations
        recommendations = []
        
        for treatment_type, stats in treatment_stats.items():
            if stats['count'] == 0:
                continue
            
            avg_similarity = stats['total_similarity'] / stats['count']
            avg_effectiveness = np.mean(stats['effectiveness_scores'])
            
            # Calculate confidence score (weighted combination)
            # Higher weight for similarity, moderate weight for effectiveness
            confidence_score = (0.7 * avg_similarity) + (0.3 * avg_effectiveness)
            
            # Calculate frequency score (normalized)
            frequency_score = min(stats['count'] / 10.0, 1.0)  # Cap at 1.0
            
            # Final score combination
            final_score = (0.6 * confidence_score) + (0.4 * frequency_score)
            
            # Get most common details
            medications = [t['medication'] for t in stats['treatments'] if t.get('medication')]
            dosages = [t['dosage'] for t in stats['treatments'] if t.get('dosage')]
            durations = [t['duration'] for t in stats['treatments'] if t.get('duration')]
            
            # Find most common values
            from collections import Counter
            common_medication = Counter(medications).most_common(1)[0][0] if medications else None
            common_dosage = Counter(dosages).most_common(1)[0][0] if dosages else None
            common_duration = Counter(durations).most_common(1)[0][0] if durations else None
            
            recommendations.append({
                'treatment_type': treatment_type,
                'frequency': stats['count'],
                'average_similarity': round(avg_similarity, 3),
                'average_effectiveness': round(avg_effectiveness, 3),
                'confidence_score': round(final_score, 3),
                'suggested_medication': common_medication,
                'suggested_dosage': common_dosage,
                'suggested_duration': common_duration,
                'based_on_cases': len(set(t['case_similarity'] for t in stats['treatments']))
            })
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return recommendations
    
    def save_model(self, filepath=None):
        """Save the trained model to disk"""
        if filepath is None:
            filepath = self.model_path
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'scaler': self.scaler,
            'similarity_threshold': self.similarity_threshold
        }
        
        joblib.dump(model_data, filepath)
        
        return filepath
    
    def load_model(self, filepath=None):
        """Load a trained model from disk"""
        if filepath is None:
            filepath = self.model_path
        
        if not os.path.exists(filepath):
            current_app.logger.warning(f"Model file not found: {filepath}")
            return False
        
        try:
            model_data = joblib.load(filepath)
            self.vectorizer = model_data['vectorizer']
            self.scaler = model_data['scaler']
            self.similarity_threshold = model_data.get('similarity_threshold', 0.3)
            return True
        except Exception as e:
            current_app.logger.error(f"Error loading model: {str(e)}")
            return False
    
    def batch_process_cases(self, cases, batch_size=100):
        """Process cases in batches for efficiency"""
        recommendations_by_case = {}
        
        for i in range(0, len(cases), batch_size):
            batch = cases[i:i + batch_size]
            
            for j, case in enumerate(batch):
                # Use other cases in batch as comparison set
                comparison_cases = batch[:j] + batch[j+1:]
                
                if comparison_cases:
                    similar_cases = self.find_similar_cases(
                        case, comparison_cases, top_n=3
                    )
                    
                    if similar_cases:
                        recommendations = self.generate_treatment_recommendations(similar_cases)
                        recommendations_by_case[case.get('case_id', f'case_{i+j}')] = recommendations
        
        return recommendations_by_case