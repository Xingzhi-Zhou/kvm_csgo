from memflow import *
import json

def load_offset(filename = "csgo.json"):
    with open(filename) as f:
        offset = json.load(f)
    return offset

def load_game():
    inventory = Inventory()
    connector = inventory.create_connector(name="qemu", args="win10")
    os = inventory.create_os(name="win32", input=connector)
    csgo = os.process_from_name("csgo.exe")
    return csgo

def load_client_base(csgo):
    client = csgo.module_by_name("client.dll")
    client_base = client.base
    return client_base

def load_engine_base(csgo):
    engine = csgo.module_by_name("engine.dll")
    engine_base = engine.base
    return engine_base

def get_players(csgo, client_base, offset, local_player = 0):
    # get player list
    players = {}
    my_flag = False
    entity_list_addr = client_base + offset["signatures"]["dwEntityList"]
    entity_addr = entity_list_addr
    while entity_addr:
        player_addr = csgo.read(entity_addr, c_uint32)
        if not player_addr:
            # print("ERROR: Not find player!")
            break
        player_id = csgo.read(entity_addr + 0x04, c_uint32)
        if player_id in players:
            # print("LOG: Find %d players." % len(players))
            break
        re_entity_addr = csgo.read(entity_addr + 0x08, c_uint32)
        next_entity_addr = csgo.read(entity_addr + 0x0c, c_uint32)

        team = csgo.read(player_addr + offset["netvars"]["m_iTeamNum"], c_int32)
        health = csgo.read(player_addr + offset["netvars"]["m_iHealth"], c_int32)
        pos_x = csgo.read(player_addr + offset["netvars"]["m_vecOrigin"], c_float)
        pos_y = csgo.read(player_addr + offset["netvars"]["m_vecOrigin"] + 0x04, c_float)
        pos_z = csgo.read(player_addr + offset["netvars"]["m_vecOrigin"] + 0x08, c_float)

        if player_addr and not(pos_x==0 and pos_y==0 and pos_z==0) and (team == 2 or team == 3) :
            if player_addr == local_player:
                my_flag = True
            player_info = [player_id, team, health, pos_x, pos_y, pos_z, my_flag]
            players[player_id] = player_info
            my_flag = False
            
        entity_addr = next_entity_addr

    # print("LOG: Find %d players." % len(players))
    return players

def get_Local_player(csgo, client_base, offset):
    local_player = csgo.read(client_base+ offset["signatures"]["dwLocalPlayer"], c_uint32)
    return local_player

def get_map(csgo, engine_base, offset):
    client_state_addr = csgo.read(engine_base+ offset["signatures"]["dwClientState"], c_uint32)
    map_name_c = csgo.read(client_state_addr + offset["signatures"]["dwClientState_Map"], c_char*30)
    map_name = ""
    for i in map_name_c:
        if i:
            map_name += chr(i)
        else:
            break
    return map_name

if __name__ == '__main__':
    offset = load_offset()
    csgo = load_game()
    engine_base = load_engine_base(csgo)
    client_base = load_client_base(csgo)

    map_name = get_map(csgo, engine_base, offset)
    print(map_name)

    local_player = get_Local_player(csgo, client_base, offset)
    # print(hex(local_player))

    players = get_players(csgo, client_base, offset, local_player)
    print("LOG: Find %d players." % len(players))
    # print(players)