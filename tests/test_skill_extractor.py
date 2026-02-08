import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.skill_extractor import SkillExtractor

def test_skill_extraction():
    """Test basic skill extraction"""
    extractor = SkillExtractor()
    
    test_cases = [
        {
            "input": "Need Python and SQL experience",
            "expected": ["python", "sql"]
        },
        {
            "input": "Machine learning with TensorFlow required",
            "expected": ["machine learning", "tensorflow"]
        },
        {
            "input": "AWS and Docker knowledge is a plus",
            "expected": ["aws", "docker"]
        }
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases):
        result = extractor.extract_skills(test["input"])
        result_lower = [r.lower() for r in result]
        
        if set(result_lower) == set(test["expected"]):
            print(f"✅ Test {i+1} passed")
        else:
            print(f"❌ Test {i+1} failed")
            print(f"   Expected: {test['expected']}")
            print(f"   Got: {result_lower}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    if test_skill_extraction():
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed")