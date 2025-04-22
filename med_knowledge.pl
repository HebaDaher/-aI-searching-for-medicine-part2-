% --- Medicine Knowledge Base ---

treats(paracetamol, [fever, headache]).
treats(ibuprofen, [pain, inflammation, fever]).
treats(antacid, [acidity, indigestion]).
treats(antihistamine, [allergy, sneezing]).
treats(amoxicillin, [infection, sore_throat]).
treats(aspirin, [headache, chest_pain]).
treats(oral_rehydration_salts, [dehydration]).
treats(cough_syrup, [cough, sore_throat]).

% --- Helper Rules ---

treats_symptom(Medicine, Symptom) :-
    treats(Medicine, SymptomList),
    member(Symptom, SymptomList).

match_count([], _, 0).
match_count([Symptom|Rest], Medicine, Count) :-
    treats_symptom(Medicine, Symptom),
    match_count(Rest, Medicine, RestCount),
    Count is RestCount + 1.
match_count([Symptom|Rest], Medicine, Count) :-
    \\+ treats_symptom(Medicine, Symptom),
    match_count(Rest, Medicine, Count).

recommend_medicines(Symptoms, Medicine, Score) :-
    treats(Medicine, _),
    match_count(Symptoms, Medicine, Score),
    Score > 0.
