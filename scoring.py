from questions import DIMENSIONS

def calculate_readiness(answers):
    dimensions, scores = {}, []
    for name, questions in DIMENSIONS.items():
        values = [answers.get(q) for q in questions]
        if any(v not in (1,2,3,4,5) for v in values):
            dimensions[name] = None
            continue
        mean = sum(values)/len(values)
        score = ((mean-1)/4)*100
        dimensions[name] = {"mean":round(mean,2),"score":round(score,2),"answered":len(values)}
        scores.append(score)
    overall = round(sum(scores)/len(scores),2) if len(scores)==len(DIMENSIONS) else None
    return {"dimensions":dimensions,"overall_score":overall}

def interpret_score(score):
    if score is None: return "Incomplete assessment"
    if score < 25: return "Very low relative score"
    if score < 50: return "Low relative score"
    if score < 75: return "Moderate relative score"
    return "High relative score"
