# pages/producer/utils/self_learning_ai.py
import os
import json
import random
import uuid
from datetime import datetime

class SelfLearningAI:
    """Self-learning AI system for Ethiopian market analysis"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.knowledge_base = self.load_knowledge_base()
        self.learning_data = self.load_learning_data()
        
        # Ethiopian market price ranges
        self.ethiopian_price_ranges = {
            'Teff': {'min': 80, 'max': 150, 'avg': 115, 'unit': 'kg'},
            'Wheat': {'min': 45, 'max': 75, 'avg': 60, 'unit': 'kg'},
            'Barley': {'min': 35, 'max': 55, 'avg': 45, 'unit': 'kg'},
            'Coffee': {'min': 200, 'max': 400, 'avg': 300, 'unit': 'kg'},
            'Milk': {'min': 60, 'max': 90, 'avg': 75, 'unit': 'liter'},
            'Beef': {'min': 400, 'max': 600, 'avg': 500, 'unit': 'kg'},
            'Onion': {'min': 25, 'max': 45, 'avg': 35, 'unit': 'kg'},
            'Tomato': {'min': 30, 'max': 55, 'avg': 42, 'unit': 'kg'},
            'Mango': {'min': 12, 'max': 22, 'avg': 17, 'unit': 'piece'},
            'Banana': {'min': 15, 'max': 25, 'avg': 20, 'unit': 'piece'}
        }
    
    def load_knowledge_base(self):
        """Load knowledge base from disk"""
        try:
            os.makedirs("data", exist_ok=True)
            path = f"data/knowledge_base_{self.user_id}.json"
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                default = {
                    'product_knowledge': {},
                    'ethiopian_market': {},
                    'price_history': {},
                    'demand_patterns': {}
                }
                with open(path, 'w') as f:
                    json.dump(default, f, indent=2)
                return default
        except:
            return {}
    
    def load_learning_data(self):
        """Load learning data from disk"""
        try:
            os.makedirs("data", exist_ok=True)
            path = f"data/learning_data_{self.user_id}.json"
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                default = {
                    'interactions': [],
                    'learning_iterations': 0
                }
                with open(path, 'w') as f:
                    json.dump(default, f, indent=2)
                return default
        except:
            return {}
    
    def get_ethiopian_market_insights(self, product_name):
        """Get Ethiopian market insights for a product"""
        # Find closest match
        closest_match = None
        for key in self.ethiopian_price_ranges:
            if product_name.lower() in key.lower() or key.lower() in product_name.lower():
                closest_match = key
                break
        
        if closest_match:
            price_data = self.ethiopian_price_ranges[closest_match]
            current_price = random.uniform(price_data['min'], price_data['max'])
            return {
                'product': closest_match,
                'current_price': round(current_price, 2),
                'min_price': price_data['min'],
                'max_price': price_data['max'],
                'avg_price': price_data['avg'],
                'unit': price_data['unit'],
                'price_trend': random.choice(['increasing', 'stable', 'decreasing']),
                'demand_level': random.choice(['high', 'medium', 'low']),
                'seasonal_factor': random.uniform(0.8, 1.2)
            }
        else:
            return {
                'product': product_name,
                'current_price': round(random.uniform(50, 200), 2),
                'min_price': 50,
                'max_price': 200,
                'avg_price': 125,
                'unit': 'kg',
                'price_trend': 'stable',
                'demand_level': 'medium',
                'seasonal_factor': 1.0
            }
    
    def analyze_product(self, product_data):
        """Analyze a product combining user data and Ethiopian market data"""
        if not product_data:
            return None
        
        product_name = product_data.get('name', '')
        user_price = product_data.get('price', 0)
        
        # Get market data
        market_data = self.get_ethiopian_market_insights(product_name)
        market_avg = market_data.get('avg_price', 0)
        
        # Calculate price comparison
        price_comparison = {
            'user_price': user_price,
            'market_avg': market_avg,
            'difference': user_price - market_avg,
            'percentage': ((user_price - market_avg) / market_avg * 100) if market_avg > 0 else 0
        }
        
        # Determine price status
        if price_comparison['percentage'] < -10:
            price_status = 'Below Market (Good for Buyers)'
        elif price_comparison['percentage'] < 10:
            price_status = 'At Market Rate'
        else:
            price_status = 'Above Market (Premium)'
        
        # Update knowledge base
        if 'product_knowledge' not in self.knowledge_base:
            self.knowledge_base['product_knowledge'] = {}
        
        self.knowledge_base['product_knowledge'][str(uuid.uuid4())] = {
            'name': product_name,
            'price': user_price,
            'market_avg': market_avg,
            'analyzed_at': datetime.now().isoformat()
        }
        
        self.learning_data['learning_iterations'] += 1
        
        return {
            'product_name': product_name,
            'market_data': market_data,
            'price_analysis': price_comparison,
            'price_status': price_status,
            'demand_level': market_data.get('demand_level', 'medium'),
            'seasonal_factor': market_data.get('seasonal_factor', 1.0),
            'market_trend': market_data.get('price_trend', 'stable'),
            'recommended_price': round(market_avg * random.uniform(0.9, 1.1), 2),
            'profit_potential': {
                'current_profit': round(user_price - product_data.get('cost_price', 0), 2),
                'margin_percentage': round(((user_price - product_data.get('cost_price', 0)) / user_price * 100) if user_price > 0 else 0, 1)
            }
        }
    
    def predict_demand(self, product_name, region='Addis Ababa'):
        """Predict demand for a product"""
        market_data = self.get_ethiopian_market_insights(product_name)
        
        base_demand = {
            'high': 150,
            'medium': 100,
            'low': 50
        }.get(market_data.get('demand_level', 'medium'), 100)
        
        region_factors = {
            'Addis Ababa': 1.3, 'Oromia': 1.0, 'Amhara': 0.95,
            'Tigray': 0.9, 'SNNP': 0.85, 'Sidama': 0.9
        }
        region_factor = region_factors.get(region, 1.0)
        seasonal_factor = market_data.get('seasonal_factor', 1.0)
        
        daily_demand = base_demand * seasonal_factor * region_factor
        
        return {
            'daily_demand': round(daily_demand, 1),
            'weekly_demand': round(daily_demand * 7, 1),
            'monthly_demand': round(daily_demand * 30, 1),
            'demand_level': market_data.get('demand_level', 'medium'),
            'region': region,
            'region_factor': region_factor,
            'seasonal_factor': seasonal_factor,
            'confidence': min(0.7 + (self.learning_data.get('learning_iterations', 0) * 0.001), 0.95)
        }
    
    def get_price_recommendation(self, product_data):
        """Get price recommendation"""
        analysis = self.analyze_product(product_data)
        if not analysis:
            return None
        
        current_price = analysis['price_analysis']['user_price']
        market_avg = analysis['price_analysis']['market_avg']
        
        # Calculate recommended price
        seasonal = analysis.get('seasonal_factor', 1.0)
        trend = 1.05 if analysis.get('market_trend') == 'increasing' else 0.95 if analysis.get('market_trend') == 'decreasing' else 1.0
        
        recommended_price = round(market_avg * seasonal * trend, 2)
        
        return {
            'current_price': current_price,
            'recommended_price': recommended_price,
            'market_average': market_avg,
            'price_difference': recommended_price - current_price,
            'percentage_change': ((recommended_price - current_price) / current_price * 100) if current_price > 0 else 0,
            'recommendation': self._get_recommendation_text(current_price, recommended_price),
            'confidence_score': min(0.8 + (self.learning_data.get('learning_iterations', 0) * 0.001), 0.95)
        }
    
    def _get_recommendation_text(self, current, recommended):
        """Get recommendation text"""
        diff = recommended - current
        if diff > current * 0.1:
            return "📈 Increase Price - Market demand supports higher pricing"
        elif diff < -current * 0.1:
            return "📉 Decrease Price - Competitive pricing needed for market share"
        else:
            return "✅ Maintain Price - Current price is well-positioned"
