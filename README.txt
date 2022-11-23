Istruzioni per generare modello da analizzare in NuSMV:

Per poter generare il modello esistono due possibili modi di eseguire lo scrit python che si occupa di queso:

1. Generare il modello a partire da un file di testo
	
	a. Preso il file di testo "bytecode" contenente il bytecode da analizzare
	b. lanciare: python model_checker_generator.py bytecode 
	c. Inserire informazioni relative al livello di sicurezza delle variabili presenti in memoria 

2. Generale il modello senza file di test
	
	a. lanciare python model_checker_generator.py 
	b. inserire tutte le informazioni richieste dallo script per generale il modello 


3. Entrambi i modi genereranno un file .smv nominato generated_model.smv

4. all'interno della shell interattiva di NuSMV  => read_model -i generated_model.smv 