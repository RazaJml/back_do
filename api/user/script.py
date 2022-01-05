import requests
import datetime
import schedule
import time

def AutoBalancerMainFun(
    api_token, 
    loadbalancer_tag, 
    droplet_tag, 
    cpu, load1, load5, load15, min_drop, max_drop
    ):

    API_TOKEN = "e93c9340e7de74d3eaf9b5b0c003d08c6fc810829dff1f1e149c4f4c7a69b122"
    DO_API_URLS = {
        "droplets": "https://api.digitalocean.com/v2/droplets",
        "loadbalancers": "https://api.digitalocean.com/v2/load_balancers"
    }

    MAIN_LOADLANCER_TAGS = loadbalancer_tag
    MAIN_DROPLET_TAG = droplet_tag
    TIME_DELTA = 2
    THRESHOLDS = {
        "cpu": cpu,
        "load_1": load1,
        "load_5": load5,
        "load_15": load15
    }

    def getMainDropletId():
        
        main_drop_url = f"https://api.digitalocean.com/v2/droplets?tag_name={MAIN_DROPLET_TAG}"
        res = requests.get(main_drop_url, headers={
            'Authorization': f'Bearer {API_TOKEN}'})
        data = res.json()

        return data['droplets'][0]['id']

    MAIN_DROPLET_ID = getMainDropletId()

    print(f'MAIN_DROPLET_ID {MAIN_DROPLET_ID}')
    # ##########################################################
    # HELPERS
    # ##########################################################


    def printTime():
        print("Time --> ", datetime.datetime.now())

    def getActiveLBDropletIDs():
        res = requests.get(DO_API_URLS['loadbalancers'], headers={
            'Authorization': f'Bearer {API_TOKEN}'})
        res = res.json()

        if len(res['load_balancers']) < 0:
            return "LoadBalancers Not Found!!!"

        for i in range(len(res['load_balancers'])):
            if res["load_balancers"][i]['tag'] == MAIN_LOADLANCER_TAGS:
                droplet_ids = res['load_balancers'][i]['droplet_ids']
                if len(droplet_ids) < 0:
                    return "No Droplets Found In LoadBalancer"
                return droplet_ids
            else:
                return f"No {MAIN_LOADLANCER_TAGS} LoadBalancer Found!"


    def getLatestSnapshotID():
        droplet_url = f'https://api.digitalocean.com/v2/droplets/{MAIN_DROPLET_ID}/'
        res = requests.get(
            droplet_url, headers={'Authorization': f'Bearer {API_TOKEN}'})
        res = res.json()
        if len(res['droplet']['snapshot_ids']) > 0:
            return res['droplet']['snapshot_ids'][-1]
        else:
            return 0

    def createSnapshot():
        droplet_url = f'https://api.digitalocean.com/v2/droplets/{MAIN_DROPLET_ID}/actions'
        data = {"type":"snapshot","name":"New Snapshot"}
        res = requests.post(
            droplet_url,
            data, 
            headers={
                'Authorization': f'Bearer {API_TOKEN}'
            }
        )
        res = res.json()
        return res


    def deleteSnapShot():
        snapshot_url = 'https://api.digitalocean.com/v2/snapshots?resource_type=droplet'

        res = requests.get(
            snapshot_url, headers={'Authorization': f'Bearer {API_TOKEN}'})
        res = res.json()

        privous_snapshot = res['snapshots'][-2]
        delete_url = 'https://api.digitalocean.com/v2/snapshots/{privous_snapshot}'

        deleted = requests.delete(
            delete_url, headers={'Authorization': f'Bearer {API_TOKEN}'})

        return deleted

    def createDroplet():
        createSnapshot()
        deleteSnapShot()
        snapshot_id = getLatestSnapshotID()
        if snapshot_id == 0:
            print("Droplet cannot be created. Reason: No snapshot exists")
            return 0
        data = {
            "name": f'mydroplet',
            "region": "nyc1",
            "size": "s-1vcpu-1gb",
            "image": snapshot_id,
            "password": 'Qwerty,123raza',
            "tags": ["web-page", "temporary"],
        }

        res = requests.post(DO_API_URLS['droplets'], data, headers={
                            'Authorization': f'Bearer {API_TOKEN}'})
        res = res.json()
        print("Droplet created successfully", res)


    def removeDroplet():
        active_lb_droplet_ids = getActiveLBDropletIDs()
        if(len(active_lb_droplet_ids) > 1):
            url = f'https://api.digitalocean.com/v2/droplets/{active_lb_droplet_ids[-1]}'
            res = requests.delete(url, headers={
                                'Authorization': f'Bearer {API_TOKEN}'})
            # res = res.json()
            print("Droplet Deleted with ID = ", active_lb_droplet_ids[-1])


    def getCpuPercentage(droplet_id, start_time, end_time):
        stats_cpu = requests.get(
            f"https://api.digitalocean.com/v2/monitoring/metrics/droplet/cpu?host_id={droplet_id}&start={start_time}&end={end_time}",
            headers={
                'Authorization': f'Bearer {API_TOKEN}'
            }
        )
        stats_cpu = stats_cpu.json()

        results = stats_cpu['data']['result']

        total_uptime = 0
        idle_uptime = 0
        for i in range(len(results)):

            res = results[i]

            value_0 = float(res['values'][0][1])
            value_1 = float(res['values'][-1][1])
            total_uptime += (value_1 - value_0)

            if(res['metric']['mode'] == 'idle'):
                idle_uptime += (value_1 - value_0)

        non_idle_percentage = None
        if total_uptime > 0:
            idle_percentage = (idle_uptime * 100) / total_uptime
            non_idle_percentage = 100 - idle_percentage

        print("CPU percentage: ", non_idle_percentage)

        return non_idle_percentage


    def getLoadAverage(droplet_id, start_time, end_time, load_interval):

        stats_load = requests.get(
            f"https://api.digitalocean.com/v2/monitoring/metrics/droplet/load_{load_interval}?host_id={droplet_id}&start={start_time}&end={end_time}",
            headers={
                'Authorization': f'Bearer {API_TOKEN}'
            }
        )
        stats_load = stats_load.json()

        ret = None
        if len(stats_load['data']['result']) > 0:
            values = stats_load['data']['result'][0]['values']
            ret = float(values[-1][1])

        print("Load", load_interval, "values ---> ", ret)
        return ret


    def getStats(droplet_id):
        datetime_object1 = datetime.datetime.now() - datetime.timedelta(minutes=TIME_DELTA)
        datetime_object2 = datetime.datetime.now()

        seconds_since_epoch = int(datetime_object1.timestamp())
        seconds_end_epoch = int(datetime_object2.timestamp())

        print("START TIME: ", seconds_since_epoch,
            ", END TIME: ", seconds_end_epoch)

        cpu_percentage = getCpuPercentage(
            droplet_id, seconds_since_epoch, seconds_end_epoch)
        load_1 = getLoadAverage(
            droplet_id, seconds_since_epoch, seconds_end_epoch, 1)
        load_5 = getLoadAverage(
            droplet_id, seconds_since_epoch, seconds_end_epoch, 5)
        load_15 = getLoadAverage(
            droplet_id, seconds_since_epoch, seconds_end_epoch, 15)

        return {
            "cpu": cpu_percentage,
            "load_1": load_1,
            "load_5": load_5,
            "load_15": load_15
        }


    def autoBalancer():
        print("##############################################################################################")
        print("autoBalancer started: -------------------------")

        active_lb_droplet_ids = getActiveLBDropletIDs()

        if type(active_lb_droplet_ids) != str:

            print("Active LB Droplet IDs: ", active_lb_droplet_ids)

            stats = {
                "cpu": 0,
                "load_1": 0,
                "load_5": 0,
                "load_15": 0
            }

            countable_droplets = 0
            for i in range(len(active_lb_droplet_ids)):
                _stats = getStats(active_lb_droplet_ids[i])
                if _stats['cpu'] != None and _stats['load_1'] != None and _stats['load_5'] != None and _stats['load_15'] != None:
                    stats['cpu'] += _stats['cpu']
                    stats['load_1'] += _stats['load_1']
                    stats['load_5'] += _stats['load_5']
                    stats['load_15'] += _stats['load_15']
                    countable_droplets += 1

            if countable_droplets > 0:
                stats['cpu'] = stats['cpu']/countable_droplets
                stats['load_1'] = stats['load_1']/countable_droplets
                stats['load_5'] = stats['load_5']/countable_droplets
                stats['load_15'] = stats['load_15']/countable_droplets

            print("AVERAGE STATS: ", stats)

            if stats['cpu'] > THRESHOLDS['cpu'] and stats['load_5'] > THRESHOLDS['load_5'] and stats['load_15'] > THRESHOLDS['load_15']:
                if countable_droplets == len(active_lb_droplet_ids):
                    createDroplet()
                else:
                    print(
                        "New droplet will not be created as recently created droplet is spinning up")
            else:
                if countable_droplets == len(active_lb_droplet_ids):
                    removeDroplet()
                else:
                    print(
                        "New droplet will not be deleted as recently created droplet is spinning up")
        else:
            print(active_lb_droplet_ids)

    autoBalancer()

    schedule.every(5).seconds.do(printTime)
    schedule.every(1).minutes.do(autoBalancer)

    while True:
        schedule.run_pending()
        time.sleep(1)


