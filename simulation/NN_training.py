import numpy as np
import pickle
from sklearn.neural_network import MLPClassifier, MLPRegressor


### MODEL Should be a class later!
### It normalizes the data itself
def train_model(X, y, plot=False, layers=20, activation='tanh', solver='lbfgs'):
    tol = 0.0001
    max_iter = 10000
    print "I will start training now"
    # learning rate adaptive only for sgd
    reg = MLPRegressor(
        hidden_layer_sizes=(layers), activation=activation, solver=solver, alpha=0, batch_size='auto',
        learning_rate='adaptive', learning_rate_init=0.001, power_t=0.5, max_iter=10000, shuffle=True,
        random_state=0, tol=0.00001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True,
        early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08)

    y_mean = np.mean(y)
    y_std = np.std(y)
    y_norm = (y - np.mean(y)) / np.std(y)

    reg.fit(X, y_norm)
    y_pred = reg.predict(X)
    print "Loss: " + str(np.round(reg.loss_, 10))
    print "Loss MSE: " + str(np.round(np.mean(np.power(y_pred - y_norm, 2)), 10))
    temp = np.power(y_pred - y_norm, 2)

    #if plot:
    #    plt.scatter(y_norm, y_pred, s=1)
    #    plt.grid()
    #    plt.show()

    return {"reg": reg, "mean": y_mean, "std": y_std, "error": temp}


# GATE and will be infered from .LUT file name
def train_csm_model(LUT_dir, solver='lbfgs', activation='tanh', layer_size=10):
    # extract basic info from LUT_DIR name
    # extract LUT name from long directory name
    extracted_list = LUT_dir.split("/")
    for a_section in extracted_list:
        if ".lut" in a_section:
            LUT_name = a_section
            break
    #print LUT_name

    # further extract GATE_NAME, V_L, V_H, VSTEP value from LUT name
    extracted_list = LUT_name.split("_")
    for a_section in extracted_list:
        if ("INV" in a_section) or ("NAND2" in a_section):
            GATE_NAME = a_section
        if "VL" in a_section:
            V_L = float(a_section[2:])
        if "VH" in a_section:
            V_H = float(a_section[2:])
        if "VSTEP" in a_section:
            VSTEP = float(a_section[5:])


    # first: load the data
    data = pickle.load(open(LUT_dir, 'r'))  # load LUT from saved .LUT file. Loaded LUT is a dict
    # this "data" should really be called LUT

    #------------------------- Saeed work from here -----------------------#
    if GATE_NAME == "INV":
        print "Training for INV is not working for now"
        '''
        y = data["I_out_DC"]
        dim = y.shape[0]
        y_flat = y.flatten()
        y = y_flat
        X = np.zeros((len(y_flat), 2))
        print "DATA SIZE IS: ", X.shape
        for i in range(len(X)):
            X[i,0] = np.round(int(i/dim)*VSTEP + V_L,3) # Vin
            X[i,1] = np.round(int(i%dim)*VSTEP + V_L,3)  # Vout
        '''

    if GATE_NAME == "NAND2":
        y = data["I_out_DC"] # y is now a nd array
        dim = y.shape[0]
        y_flat = y.flatten()
        y = y_flat # y is now a flat array
        X = np.zeros((len(y_flat), 4))
        print "DATA SIZE IS: ", X.shape




        print "----- making X ----"
        vec = [np.round(idx*VSTEP+V_L, 2) for idx in range(0, dim)]
        mg = np.array(np.meshgrid(vec, vec, vec, vec))
        mg2 = np.transpose(mg, (2, 1, 3, 4, 0))
        temp = mg2.reshape(-1,4)
        X = temp
        print "--- done here ---- "
        # for i in range(len(X)):
        #     vec = [np.round(idx*VSTEP+V_L, 2) for idx in range(0, dim)]
        #     mg = np.array(np.meshgrid(vec, vec, vec, vec))
        #     mg2 = np.transpose(mg, (2, 1, 3, 4, 0))
        #     temp = mg2.reshape(-1,4)
        # The order is: [Vna, Vnb, Vn1, Vout]
        # X[i,0] = (int(i/(dim*dim*dim))%dim)*VSTEP + V_L # Vna
        # X[i,1] = (int(i/(dim*dim))%dim)*VSTEP + V_L # Vnb
        # X[i,2] = (int(i/dim)%dim)*VSTEP + V_L # Vn1
        # X[i,3] = int(i%dim)*VSTEP + V_L # Vout


    print "salam"
    print GATE_NAME
    # start = datetime.datetime.now()
    print "Training NN model for NAND2",
    model = train_model(X, y, solver='lbfgs', activation='tanh', layers=20)
    print "Model has been trained"#, and it took the system: " #, datetime.datetime.now() - start

    # return model
    print("Dumping NN model to .nn file in LUT_bin...")
    pickle.dump(model, open(LUT_dir[:-4] + ".nn", 'w'))