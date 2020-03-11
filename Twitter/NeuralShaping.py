from SQLiteDB import SQLiteDB
from NeuralNet import NeuralNet

from pathlib import Path
from matplotlib import pyplot as plt

#TODO clean this gross file up, add inputs
class NeuralShaping():

    def __init__(self, db_wrapper):
        data = db_wrapper.get_all()

        #remove data if count of hour < 25
        counts = data['hour'].value_counts()
        data = data[~data['hour'].isin(counts[counts < 25].index)]

        data = data.sample(frac=1).reset_index(drop=True)
        outputs = data[['wait_time']].to_numpy()
        data = data[['hour', 'weekday', 'day']].to_numpy()

        nets = list()
        models = list()
        start_shape = ()
        epoch_lim = 200
        for node_size in [pow(2, x) for x in range(9, 10)]:
            for middle_layers in range(2, 3):
                #model setup
                start_shape = (3,) + (node_size,)*middle_layers
                net = NeuralNet(shape=start_shape)
                graphs_path = Path(__file__).parent.parent
                graphs_dir = graphs_path.joinpath( 'AutoGraphs/{}/'.format('-'.join([str(x) for x in start_shape]))).resolve()
                models.append(net)
                net.set_rounding(0.25)
                net.set_train_test_val(0.7, 0.2, 0.1)
                net.train_model(data=data, labels=outputs, epochs=epoch_lim, weights_path = graphs_dir)
                nets.append((net, start_shape, epoch_lim))


                #model graph output
                print_data=db_wrapper.get_all()

                counts = print_data['hour'].value_counts()
                print_data = print_data[~print_data['hour'].isin(counts[counts < 25].index)]

               
                for month in range(6, 13):
                    #filter by day of week
                    queried = print_data.loc[print_data['month'] == month]
                    queried = queried.loc[queried['year'] == 2019]
                    
                    #get mean of expected wait times, grouped by weekday and hour
                    val_expect = list(queried.groupby(['day', 'hour']).mean()['wait_time'])

                    #create input data for net
                    
                    val_data = queried.groupby(['day', 'hour']).mean().reset_index()[['hour', 'weekday', 'day']].to_numpy()
                    run_outputs = net.model.predict(val_data)

                    
                    graphs_dir.mkdir(exist_ok=True, parents=True)

                   
                    plt.figure(figsize=(20,10))
                    plt.plot(val_expect, '--bo', label='actual vals')
                    plt.plot(run_outputs, '--ro', label='predicted vals')
                    plt.legend()
                    plt.savefig(graphs_dir.joinpath('fig_month_{}.pdf'.format(month)))
                    plt.close('all')

                for day in range(1, 7):
                    #filter by day of week
                    queried = print_data.loc[print_data['weekday'] == day]
                    
                    #get mean of expected wait times, grouped by weekday and hour
                    val_expect = list(queried.groupby(['weekday', 'hour']).mean()['wait_time'])

                    #create input data for net
                    
                    val_data = queried.groupby(['weekday', 'hour']).mean().reset_index()[['hour', 'weekday', 'day']].to_numpy()
                    run_outputs = net.model.predict(val_data)

                    plt.plot(val_data[:,0], val_expect, '--bo', label='actual vals')
                    plt.plot(val_data[:,0], run_outputs, '--ro', label='predicted vals')
                    plt.legend()
                    plt.savefig(graphs_dir.joinpath('fig_day_{}.pdf'.format(day)))
                    plt.close('all')

                with open(graphs_dir.joinpath('results.txt'), 'w') as file_:
                    file_.write('{}\t{}\t{}\n'.format(start_shape, net.avg, net.worst))


        for net, start_shape, epochs in nets:
            print(epochs, start_shape, net.avg, net.worst)

