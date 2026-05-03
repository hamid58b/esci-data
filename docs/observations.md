# Observations

I ran with 2 different modesl, got different resutls:

with 4o-mini and gpt-5.4-mini. Temperature is 0.0 for both.

```
python3 main.py                      
Audit set size: 24 rows
Results written to /Users/hamidbagheri/GitHub/temp/esci-data/label_audit/output/results.csv

Total pairs audited : 24
Accurate ('E' correct): 13
Mislabeled           : 11

Mislabeled rows:
 query_id product_id                           reformulated_query
     6014 B00LHSAARW                         aa batteries 60 pack
     6014 B00KMDL8U6 Energizer AA Max Alkaline Batteries 50 count
     6014 B01B8R6V2E                       AAA batteries 100 pack
    32814 B07TWK2S22      dewalt 12v max cordless screwdriver kit
    32814 B0812ZHY5N       dewalt 8v max cordless screwdriver kit
    32814 B00EUHAGX0                dewalt 8v max battery charger
    58953 B085F42SV6             kodak photo paper 8.5 x 11 matte
    58953 B01M0L2WLF kodak photo paper 8.5 x 11 glossy 100 sheets
    58953 B01JB7D4SW kodak photo paper 8.5 x 11 glossy 100 sheets
    58953 B000EZTYHG  kodak photo paper 8.5 x 11 glossy 50 sheets
    58953 B000EZ0CTK             kodak photo paper 8.5 x 11 matte
(.venv) hamidbagheri@HBM label_audit % python3 main.py
Audit set size: 24 rows
Results written to /Users/hamidbagheri/GitHub/temp/esci-data/label_audit/output/results.csv

Total pairs audited : 24
Accurate ('E' correct): 17
Mislabeled           : 7

Mislabeled rows:
 query_id product_id                                    reformulated_query
     6014 B00LHSAARW                                  AA batteries 60 pack
     6014 B01B8R6V2E                                aaa batteries 100 pack
    32814 B07TWK2S22                   DEWALT 12V MAX cordless screwdriver
    32814 B0812ZHY5N Enertwist 8V max cordless screwdriver kit, gyroscopic
    32814 B00EUHAGX0                         dewalt 8v max battery charger
    58953 B085F42SV6            kodak photo paper 8.5 x 11 matte 100 count
    58953 B000EZ0CTK                      Kodak photo paper 8.5 x 11 matte
(.venv) hamidbagheri@HBM label_audit % 

```

## TODO

- use reasoner model to validate the results.
- use different model and aggregate / ensemble the results via majority voting.
- needs SME-validations or poroduct knowledge base (RAG or taxonomy) to be sure about the results.
