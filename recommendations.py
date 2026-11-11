RECOMMENDATIONS = {
"Technology and Data Readiness":["Review technology infrastructure availability and reliability.","Assess data quality, accessibility, integration, and management.","Identify technical requirements for AI applications."],
"Organizational Readiness":["Clarify management responsibilities for AI initiatives.","Review how AI is incorporated into digital transformation plans.","Assess resources and coordination between departments."],
"People and Skills Readiness":["Identify employees' current AI knowledge and skills.","Consider targeted AI awareness and training.","Assess opportunities to develop AI-related skills."],
"Governance and Regulatory Readiness":["Review policies governing data collection, access, and use.","Consider AI risk assessment and ethical oversight procedures.","Review data protection and AI monitoring mechanisms."],
"Public Service and Value Readiness":["Identify public services where AI may provide measurable value.","Consider accessibility, service quality, and responsiveness.","Assess public trust and potential effects on citizens."]}

def generate_recommendations(results):
    valid={k:v["score"] for k,v in results.items() if v is not None}
    if not valid: return {}
    avg=sum(valid.values())/len(valid)
    return {k:RECOMMENDATIONS[k] for k,v in valid.items() if v<avg}
