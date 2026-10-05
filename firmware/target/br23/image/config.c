#include "system/includes.h"
#include "syscfg_id.h"
/* Keep the vendor calibration/MAC IDs in their dedicated region. */
const struct btif_item btif_table[] = {
    {CFG_BT_MAC_ADDR, 6}, {CFG_BT_FRE_OFFSET, 6}, {0, 0}
};
const int vm_max_size_config = 65536;
