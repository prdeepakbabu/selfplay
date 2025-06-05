"""
Conversation analyzer for detecting when a conversation has naturally concluded.
"""

import re
from collections import Counter
import string

class ConversationAnalyzer:
    def __init__(self, end_threshold=0.6):
        """
        Initialize the conversation analyzer.
        
        Args:
            end_threshold: Threshold score (0-1) to determine when a conversation has ended.
        """
        self.end_threshold = end_threshold
        self.farewell_phrases = [
            # Standard farewells
            "goodbye", "bye", "thank you for your help", "that's all", 
            "have a good day", "thanks for your assistance", "thanks for your help",
            "thank you for the information", "i appreciate your help",
            "that answers my question", "that's what i needed to know",
            "i have no more questions", "that's it for now", "until next time",
            "have a nice day", "take care", "farewell", "see you later",
            "thanks again", "this has been helpful", "this was helpful",
            
            # Meta-conversation endings
            "conversation has reached its conclusion", "reached its logical conclusion",
            "conversation has ended", "end of this conversation", 
            "ready for your next instruction", "ready for the next query",
            "standing by", "standing by to assist", "wait for genuine human input",
            "wait for your next question", "ready to move on", 
            "this exchange is complete", "this interaction has concluded",
            
            # Acknowledgment of conversation state
            "unusual situation", "unusual exchange", "unusual interaction",
            "unusual circumstance", "reached an impasse", "conversation loop",
            "break this pattern", "break this loop",
            
            # Simple thank you variations
            "thank you", "thanks", "appreciate", "grateful"
        ]
        
    def detect_end_signals(self, conversation_history, current_turn):
        """
        Analyze the conversation to detect end signals.
        
        Args:
            conversation_history: List of conversation turns as tuples (bot_name, message, response)
            current_turn: The current turn number
            
        Returns:
            tuple: (should_end, confidence_score, reason)
        """
        # Skip early detection for the first few turns
        if current_turn < 2:
            return False, 0.0, "Too early in conversation"
            
        # Get the last few messages for analysis
        recent_messages = conversation_history[-2:]
        
        # Get more context for meta-conversation detection
        extended_context = conversation_history[-4:] if len(conversation_history) >= 4 else conversation_history
        
        # Calculate individual signal scores
        farewell_score = self._detect_farewells(recent_messages)
        repetition_score = self._detect_repetition(conversation_history)
        resolution_score = self._detect_resolution(recent_messages)
        meta_conversation_score = self._detect_meta_conversation(extended_context)
        waiting_pattern_score = self._detect_waiting_pattern(extended_context)
        
        # Combine scores (weighted average)
        combined_score = (farewell_score * 0.3 + 
                         repetition_score * 0.2 + 
                         resolution_score * 0.2 +
                         meta_conversation_score * 0.2 +
                         waiting_pattern_score * 0.1)
        
        # Determine the primary reason
        reason = self._determine_primary_reason(
            farewell_score, repetition_score, resolution_score,
            meta_conversation_score, waiting_pattern_score)
        
        # Check if the combined score exceeds the threshold
        should_end = combined_score >= self.end_threshold
        
        return should_end, combined_score, reason
    
    def _detect_farewells(self, recent_messages):
        """
        Detect farewell phrases in recent messages.
        
        Args:
            recent_messages: List of recent conversation turns
            
        Returns:
            float: Score between 0-1 indicating presence of farewell signals
        """
        score = 0.0
        
        # Check the last two messages for farewell phrases
        for _, _, message in recent_messages:
            message_lower = message.lower()
            
            # Check for exact farewell phrases
            for phrase in self.farewell_phrases:
                if phrase in message_lower:
                    score += 0.5
            
            # Check for gratitude expressions with more variations
            if re.search(r'thank(s| you)|appreciate|grateful', message_lower):
                score += 0.3
                
            # Check for closure indicators with more variations
            if re.search(r'that\'s (all|it)|no (more|other) questions|conclude|conclusion|end|finish', message_lower):
                score += 0.4
                
            # Check for waiting indicators
            if re.search(r'(wait|ready) for (your|the next|human|genuine)', message_lower):
                score += 0.5
                
            # Check for acknowledgment of conversation state
            if re.search(r'(unusual|strange|peculiar) (situation|exchange|interaction|circumstance)', message_lower):
                score += 0.3
        
        # Cap the score at 1.0
        return min(score, 1.0)
        
    def _detect_repetition(self, conversation_history):
        """
        Detect repetitive patterns in the conversation.
        
        Args:
            conversation_history: Full conversation history
            
        Returns:
            float: Score between 0-1 indicating repetition
        """
        if len(conversation_history) < 4:
            return 0.0
            
        # Extract the last 4 messages
        last_messages = [self._normalize_text(msg[2]) for msg in conversation_history[-4:]]
        
        # Check for exact repetition
        if len(set(last_messages)) < len(last_messages):
            return 1.0
            
        # Check for semantic similarity using n-grams
        similarity_scores = []
        for i in range(len(last_messages) - 1):
            for j in range(i + 1, len(last_messages)):
                similarity = self._calculate_text_similarity(last_messages[i], last_messages[j])
                similarity_scores.append(similarity)
                
        # Average similarity score
        if similarity_scores:
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            # Scale: 0.7+ similarity is considered repetitive
            if avg_similarity > 0.7:
                return (avg_similarity - 0.7) * 3.33  # Scale to 0-1 range
                
        return 0.0
        
    def _detect_resolution(self, recent_messages):
        """
        Detect if the conversation topic has been resolved.
        
        Args:
            recent_messages: List of recent conversation turns
            
        Returns:
            float: Score between 0-1 indicating topic resolution
        """
        score = 0.0
        
        # Check the last message for resolution indicators
        _, _, last_message = recent_messages[-1]
        last_message_lower = last_message.lower()
        
        # Check for question marks in the last message (indicates unresolved questions)
        if '?' in last_message:
            return 0.0  # New questions mean the conversation isn't resolved
            
        # Check for resolution phrases
        resolution_phrases = [
            "hope that helps", "hope this helps", "hope that answered", 
            "hope this answered", "that should address", "that covers", 
            "as requested", "as you asked", "as mentioned"
        ]
        
        for phrase in resolution_phrases:
            if phrase in last_message_lower:
                score += 0.3
                
        # Check for summary indicators
        if re.search(r'in summary|to summarize|in conclusion|to recap', last_message_lower):
            score += 0.4
            
        # Check if the message is short (often indicates conversation winding down)
        if len(last_message.split()) < 20:
            score += 0.2
            
        # Cap the score at 1.0
        return min(score, 1.0)
        
    def _detect_meta_conversation(self, messages):
        """
        Detect meta-conversation about the conversation itself ending.
        
        Args:
            messages: List of recent conversation turns
            
        Returns:
            float: Score between 0-1 indicating presence of meta-conversation
        """
        score = 0.0
        
        # Keywords that indicate meta-conversation about ending
        meta_keywords = [
            "conversation", "exchange", "interaction", "discussion",
            "conclude", "conclusion", "end", "finished", "complete",
            "impasse", "loop", "pattern", "test", "scenario"
        ]
        
        for _, _, message in messages:
            message_lower = message.lower()
            
            # Count meta-conversation keywords
            keyword_count = sum(1 for keyword in meta_keywords if keyword in message_lower)
            
            # If multiple meta-conversation keywords are present, likely discussing the conversation itself
            if keyword_count >= 2:
                score += 0.4
                
            # Check for explicit mentions of conversation state
            if re.search(r'(this|the) conversation (has|is|seems|appears)', message_lower):
                score += 0.5
                
            # Check for references to both participants being AI or assistants
            if re.search(r'(both|two|we are) (ai|assistant|claude)', message_lower):
                score += 0.6
        
        # Cap the score at 1.0
        return min(score, 1.0)
        
    def _detect_waiting_pattern(self, messages):
        """
        Detect patterns where both participants indicate they're waiting for new input.
        
        Args:
            messages: List of recent conversation turns
            
        Returns:
            float: Score between 0-1 indicating presence of waiting pattern
        """
        score = 0.0
        waiting_indicators = 0
        
        for _, _, message in messages:
            message_lower = message.lower()
            
            # Check for waiting indicators
            if re.search(r'(wait|ready|standing by) for (your|the next|human|genuine|new)', message_lower):
                waiting_indicators += 1
                
            # Check for statements about needing external input
            if re.search(r'(need|require|wait for) (human|user|new|next) (input|query|question|instruction)', message_lower):
                waiting_indicators += 1
        
        # If multiple waiting indicators are found across messages, likely both participants are waiting
        if waiting_indicators >= 2:
            score = 0.8
        elif waiting_indicators == 1:
            score = 0.4
            
        return score
        
    def _determine_primary_reason(self, farewell_score, repetition_score, resolution_score, meta_conversation_score, waiting_pattern_score):
        """
        Determine the primary reason for ending the conversation.
        
        Args:
            farewell_score: Score for farewell detection
            repetition_score: Score for repetition detection
            resolution_score: Score for resolution detection
            meta_conversation_score: Score for meta-conversation detection
            waiting_pattern_score: Score for waiting pattern detection
            
        Returns:
            str: Primary reason for ending the conversation
        """
        scores = {
            "Farewell detected": farewell_score,
            "Repetitive conversation": repetition_score,
            "Topic resolved": resolution_score,
            "Meta-conversation about ending": meta_conversation_score,
            "Both participants waiting for input": waiting_pattern_score
        }
        
        # Find the reason with the highest score
        primary_reason = max(scores.items(), key=lambda x: x[1])
        
        if primary_reason[1] > 0.3:  # Only return a reason if the score is significant
            return primary_reason[0]
        else:
            return "Multiple factors"
            
    def _normalize_text(self, text):
        """
        Normalize text for comparison by removing punctuation and converting to lowercase.
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text
        """
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text
        
    def _calculate_text_similarity(self, text1, text2):
        """
        Calculate similarity between two texts using n-gram overlap.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Similarity score between 0-1
        """
        # Generate word n-grams
        def get_ngrams(text, n=2):
            words = text.split()
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
            
        # Get bigrams and trigrams
        bigrams1 = set(get_ngrams(text1, 2))
        bigrams2 = set(get_ngrams(text2, 2))
        trigrams1 = set(get_ngrams(text1, 3))
        trigrams2 = set(get_ngrams(text2, 3))
        
        # Calculate Jaccard similarity
        def jaccard(set1, set2):
            if not set1 or not set2:
                return 0.0
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            return intersection / union if union > 0 else 0.0
            
        # Combine bigram and trigram similarities
        bigram_sim = jaccard(bigrams1, bigrams2)
        trigram_sim = jaccard(trigrams1, trigrams2)
        
        # Weight trigrams more heavily as they capture more context
        return (bigram_sim * 0.4) + (trigram_sim * 0.6)
