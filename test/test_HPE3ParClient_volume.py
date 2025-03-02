# (c) Copyright 2015-2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test class of 3PAR Client handling volume & snapshot."""

import time
import unittest
from pytest_testconfig import config
from test import HPE3ParClient_base as hpe3parbase

from hpe3parclient import exceptions


CPG_NAME1 = 'CPG1_UNIT_TEST' + hpe3parbase.TIME
CPG_NAME2 = 'CPG2_UNIT_TEST' + hpe3parbase.TIME
VOLUME_NAME1 = 'VOLUME1_UNIT_TEST' + hpe3parbase.TIME
VOLUME_NAME2 = 'VOLUME2_UNIT_TEST' + hpe3parbase.TIME
VOLUME_NAME3 = 'VOLUME3_UNIT_TEST' + hpe3parbase.TIME
SNAP_NAME1 = 'SNAP_UNIT_TEST1' + hpe3parbase.TIME
SNAP_NAME2 = 'SNAP_UNIT_TEST2' + hpe3parbase.TIME
DOMAIN = 'UNIT_TEST_DOMAIN'
VOLUME_SET_NAME1 = 'VOLUME_SET1_UNIT_TEST' + hpe3parbase.TIME
VOLUME_SET_NAME2 = 'VOLUME_SET2_UNIT_TEST' + hpe3parbase.TIME
VOLUME_SET_NAME3 = 'VOLUME_SET3_UNIT_TEST' + hpe3parbase.TIME
VOLUME_SET_NAME4 = 'VSET_' + hpe3parbase.TIME
SIZE = 512
REMOTE_COPY_GROUP_NAME1 = 'RCG1_UNIT_TEST' + hpe3parbase.TIME
REMOTE_COPY_GROUP_NAME2 = 'RCG2_UNIT_TEST' + hpe3parbase.TIME
REMOTE_COPY_TARGETS = [{"targetName": "testTarget",
                        "mode": 2,
                        "roleReversed": False,
                        "groupLastSyncTime": None}]
RC_VOLUME_NAME = 'RC_VOLUME1_UNIT_TEST' + hpe3parbase.TIME
SCHEDULE_NAME1 = 'SCHEDULE_NAME1' + hpe3parbase.TIME
SCHEDULE_NAME2 = 'SCHEDULE_NAME2' + hpe3parbase.TIME
SKIP_RCOPY_MESSAGE = ("Only works with flask server.")
SKIP_FLASK_RCOPY_MESSAGE = ("Remote copy is not configured to be tested "
                            "on live arrays.")
TARGET_NAME = 'testtarget'
SOURCE_PORT = '1:1:1'
TARGET_PORT = '10.10.10.1'
RCOPY_STARTED = 3
RCOPY_STOPPED = 5
FAILOVER_GROUP = 7
RESTORE_GROUP = 10
MODE = 'sync'
TPVV = 1
FPVV = 2
TDVV = 3
CONVERT_TO_DECO = 4
INVALID_PROVISIONING_TYPE = 5
USR_CPG = 1
INVALID_CPG = 3
VOLUME_PAIR_LIST = {'volumePairs': [{'sourceVolumeName': 'primary_vol1',
                                     'targetVolumeName': 'secondary_vol1'},
                                    {'sourceVolumeName': 'primary_vol2',
                                     'targetVolumeName': 'secondary_vol2'}]}


def is_live_test():
    return config['TEST']['unit'].lower() == 'false'


def no_remote_copy():
    unit_test = config['TEST']['unit'].lower() == 'false'
    remote_copy = config['TEST']['run_remote_copy'].lower() == 'true'
    run_remote_copy = not remote_copy or not unit_test
    return run_remote_copy


class HPE3ParClientVolumeTestCase(hpe3parbase.HPE3ParClientBaseTestCase):

    def setUp(self):
        super(HPE3ParClientVolumeTestCase, self).setUp(withSSH=True)

        optional = self.CPG_OPTIONS
        try:
            self.cl.createCPG(CPG_NAME1, optional)
        except Exception:
            pass
        try:
            self.cl.createCPG(CPG_NAME2, optional)
        except Exception:
            pass
        try:
            self.secondary_cl.createCPG(CPG_NAME1, optional)
        except Exception:
            pass
        try:
            self.secondary_cl.createCPG(CPG_NAME2, optional)
        except Exception:
            pass

    def tearDown(self):

        try:
            self.cl.deleteVolume(SNAP_NAME1)
        except Exception:
            pass
        try:
            self.cl.deleteVolume(SNAP_NAME2)
        except Exception:
            pass
        try:
            self.cl.deleteVolumeSet(VOLUME_SET_NAME1)
        except Exception:
            pass
        try:
            self.cl.deleteVolumeSet(VOLUME_SET_NAME2)
        except Exception:
            pass
        try:
            self.cl.deleteVolumeSet(VOLUME_SET_NAME3)
        except Exception:
            pass
        try:
            self.cl.deleteVolume(VOLUME_NAME1)
        except Exception:
            pass
        try:
            self.cl.deleteVolume(VOLUME_NAME2)
        except Exception:
            pass
        try:
            self.cl.deleteVolume(VOLUME_NAME3)
        except Exception:
            pass
        try:
            self.cl.deleteCPG(CPG_NAME1)
        except Exception:
            pass
        try:
            self.cl.deleteCPG(CPG_NAME2)
        except Exception:
            pass
        try:
            self.cl.stopRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        except Exception:
            pass
        try:
            self.cl.removeVolumeFromRemoteCopyGroup(
                REMOTE_COPY_GROUP_NAME1, RC_VOLUME_NAME, removeFromTarget=True,
                useHttpDelete=False)
        except Exception:
            pass
        try:
            self.cl.removeRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        except Exception:
            pass
        try:
            self.cl.deleteVolume(RC_VOLUME_NAME)
        except Exception:
            pass
        try:
            self.secondary_cl.deleteVolume(RC_VOLUME_NAME)
        except Exception:
            pass
        try:
            self.secondary_cl.deleteCPG(CPG_NAME1)
        except Exception:
            pass
        try:
            self.secondary_cl.deleteCPG(CPG_NAME2)
        except Exception:
            pass

        super(HPE3ParClientVolumeTestCase, self).tearDown()

    def test_1_create_volume(self):
        self.printHeader('create_volume')

        # add one
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # check
        vol1 = self.cl.getVolume(VOLUME_NAME1)
        self.assertIsNotNone(vol1)
        volName = vol1['name']
        self.assertEqual(VOLUME_NAME1, volName)

        # add another
        optional = {'comment': 'test volume2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME2, SIZE, optional)

        # check
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        self.assertIsNotNone(vol2)
        volName = vol2['name']
        comment = vol2['comment']
        self.assertEqual(VOLUME_NAME2, volName)
        self.assertEqual("test volume2", comment)

        self.printFooter('create_volume')

    def test_1_create_volume_badParams(self):
        self.printHeader('create_volume_badParams')

        name = VOLUME_NAME1
        cpgName = CPG_NAME1
        optional = {'id': 4, 'comment': 'test volume', 'badPram': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            name,
            cpgName,
            SIZE,
            optional)

        self.printFooter('create_volume_badParams')

    def test_1_create_volume_duplicate_name(self):
        self.printHeader('create_volume_duplicate_name')

        # add one and check
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        self.assertRaises(
            exceptions.HTTPConflict,
            self.cl.createVolume,
            VOLUME_NAME1,
            CPG_NAME2,
            SIZE,
            optional
        )

        self.printFooter('create_volume_duplicate_name')

    def test_1_create_volume_tooLarge(self):
        self.printHeader('create_volume_tooLarge')

        optional = {'id': 3, 'comment': 'test volume', 'tpvv': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            VOLUME_NAME1,
            CPG_NAME1,
            16777218,
            optional
        )

        self.printFooter('create_volume_tooLarge')

    def test_1_create_volume_duplicate_ID(self):
        self.printHeader('create_volume_duplicate_ID')

        optional = {'id': 10000, 'comment': 'first volume'}
        optional2 = {'id': 10000, 'comment': 'volume with duplicate ID'}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        self.assertRaises(
            exceptions.HTTPConflict,
            self.cl.createVolume,
            VOLUME_NAME2,
            CPG_NAME2,
            SIZE,
            optional2
        )

        self.printFooter('create_volume_duplicate_ID')

    def test_1_create_volume_longName(self):
        self.printHeader('create_volume_longName')

        optional = {'id': 5}
        LongName = ('ThisVolumeNameIsWayTooLongToMakeAnySenseAndIs'
                    'DeliberatelySo')
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            LongName,
            CPG_NAME1,
            SIZE,
            optional
        )

        self.printFooter('create_volume_longName')

    def test_2_get_volume_bad(self):
        self.printHeader('get_volume_bad')

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getVolume,
            'NoSuchVolume'
        )

        self.printFooter('get_volume_bad')

    def test_2_get_volumes(self):
        self.printHeader('get_volumes')

        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE)
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE)

        vol1 = self.cl.getVolume(VOLUME_NAME1)
        vol2 = self.cl.getVolume(VOLUME_NAME2)

        vols = self.cl.getVolumes()

        self.assertTrue(self.findInDict(vols['members'], 'name', vol1['name']))
        self.assertTrue(self.findInDict(vols['members'], 'name', vol2['name']))

        self.printFooter('get_volumes')

    def test_3_delete_volume_nonExist(self):
        self.printHeader('delete_volume_nonExist')

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.deleteVolume,
            VOLUME_NAME1
        )

        self.printFooter('delete_volume_nonExist')

    def test_3_delete_volumes(self):
        self.printHeader('delete_volumes')

        optional = {'comment': 'Made by flask.'}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        self.cl.getVolume(VOLUME_NAME1)

        optional = {'comment': 'Made by flask.'}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)
        self.cl.getVolume(VOLUME_NAME2)

        self.cl.deleteVolume(VOLUME_NAME1)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getVolume,
            VOLUME_NAME1
        )

        self.cl.deleteVolume(VOLUME_NAME2)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getVolume,
            VOLUME_NAME2
        )

        self.printFooter('delete_volumes')

    def test_4_create_snapshot_no_optional(self):
        self.printHeader('create_snapshot_no_optional')

        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        # add one
        self.cl.createSnapshot(SNAP_NAME1, VOLUME_NAME1)
        # no API to get and check

        self.cl.deleteVolume(SNAP_NAME1)

        self.printFooter('create_snapshot_no_optional')

    def test_4_create_snapshot(self):
        self.printHeader('create_snapshot')

        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        # add one
        optional = {'expirationHours': 300}
        self.cl.createSnapshot(SNAP_NAME1, VOLUME_NAME1, optional)
        # no API to get and check

        self.cl.deleteVolume(SNAP_NAME1)

        self.printFooter('create_snapshot')

    def test_4_create_snapshot_badParams(self):
        self.printHeader('create_snapshot_badParams')

        # add one
        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        optional = {'Bad': True, 'expirationHours': 300}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createSnapshot,
            SNAP_NAME1,
            VOLUME_NAME1,
            optional
        )

        self.printFooter('create_snapshot_badParams')

    def test_4_create_snapshot_nonExistVolume(self):
        self.printHeader('create_snapshot_nonExistVolume')

        # add one
        name = 'UnitTestSnapshot'
        volName = 'NonExistVolume'
        optional = {'id': 1, 'comment': 'test snapshot',
                    'readOnly': True, 'expirationHours': 300}
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.createSnapshot,
            name,
            volName,
            optional
        )

        self.printFooter('create_snapshot_nonExistVolume')

    def test_5_grow_volume(self):
        self.printHeader('grow_volume')

        # add one
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # grow it
        result = self.cl.growVolume(VOLUME_NAME1, 1)

        result = self.cl.getVolume(VOLUME_NAME1)
        size_after = result['sizeMiB']
        self.assertGreater(size_after, SIZE)

        self.printFooter('grow_volume')

    def test_5_grow_volume_with_float_value(self):
        self.printHeader('grow_volume_with_float_value')

        # add one
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # grow it
        result = self.cl.growVolume(VOLUME_NAME1, 1.0)

        result = self.cl.getVolume(VOLUME_NAME1)
        size_after = result['sizeMiB']
        self.assertGreater(size_after, SIZE)

        self.printFooter('grow_volume_with_float_value')

    def test_5_grow_volume_bad(self):
        self.printHeader('grow_volume_bad')

        # add one
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # shrink it
        # 3par is returning 409 instead of 400
        self.assertRaises(
            (exceptions.HTTPBadRequest, exceptions.HTTPConflict),
            self.cl.growVolume,
            VOLUME_NAME1,
            -1
        )

        self.printFooter('grow_volume_bad')

    def test_6_copy_volume(self):
        self.printHeader('copy_volume')

        # TODO: Add support for ssh/stopPhysical copy in mock mode
        if self.unitTest:
            self.printFooter('copy_volume')
            return

        # add one
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # copy it
        optional = {'online': True}
        self.cl.copyVolume(VOLUME_NAME1, VOLUME_NAME2, CPG_NAME1, optional)
        self.cl.getVolume(VOLUME_NAME2)
        self.cl.stopOnlinePhysicalCopy(VOLUME_NAME2)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getVolume,
            VOLUME_NAME2
        )

        self.printFooter('copy_volume')

    def test_6_copy_volume_invalid_volume(self):
        self.printHeader('copy_volume')

        # TODO: Add support for ssh/stopPhysical copy in mock mode
        if self.unitTest:
            self.printFooter('copy_volume')
            return

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.stopOnlinePhysicalCopy,
            "fake-volume"
        )

        self.printFooter('copy_volume')

    def test_7_copy_volume_failure(self):
        self.printHeader('copy_volume_failure')

        # add one
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)

        optional = {'online': False, 'tpvv': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.copyVolume,
            VOLUME_NAME1,
            VOLUME_NAME2,
            CPG_NAME1,
            optional)

        optional = {'online': False, 'tpdd': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.copyVolume,
            VOLUME_NAME1,
            VOLUME_NAME2,
            CPG_NAME1,
            optional)

        # destCPG isn't allowed to go to the 3PAR during an
        # offline copy.  The client strips it out, so this should pass
        optional = {'online': False, 'destCPG': 'test'}
        self.cl.copyVolume(VOLUME_NAME1, VOLUME_NAME2, CPG_NAME1, optional)
        self.cl.getVolume(VOLUME_NAME2)
        self.cl.deleteVolume(VOLUME_NAME2)
        self.cl.deleteVolume(VOLUME_NAME1)

        self.printFooter('copy_volume_failure')

    def test_7_create_volume_set(self):
        self.printHeader('create_volume_set')

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1")

        resp = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        print(resp)

        self.printFooter('create_volume_set')

    def test_7_create_volume_set_with_volumes(self):
        self.printHeader('create_volume_set')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)

        members = [VOLUME_NAME1, VOLUME_NAME2]
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1",
                                setmembers=members)

        resp = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        self.assertIsNotNone(resp)
        resp_members = resp['setmembers']
        self.assertIn(VOLUME_NAME1, resp_members)
        self.assertIn(VOLUME_NAME2, resp_members)

        self.printFooter('create_volume_set')

    def test_7_create_volume_set_dup(self):
        self.printHeader('create_volume_set_dup')

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1")

        # create it again
        self.assertRaises(
            exceptions.HTTPConflict,
            self.cl.createVolumeSet,
            VOLUME_SET_NAME1,
            domain=self.DOMAIN,
            comment="Unit test volume set 1"
        )

        self.printFooter('create_volume_set_dup')

    def test_7_add_remove_volume_in_volume_set(self):
        self.printHeader('add_remove_volume_in_volume_set')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1",
                                setmembers=None)

        # Add volume to volume set
        self.cl.addVolumeToVolumeSet(VOLUME_SET_NAME1, VOLUME_NAME1)

        resp = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        self.assertIsNotNone(resp)
        resp_members = resp['setmembers']
        self.assertIn(VOLUME_NAME1, resp_members)

        # Remove volume from volume set
        self.cl.removeVolumeFromVolumeSet(VOLUME_SET_NAME1, VOLUME_NAME1)

        # Check that None is returned if no volume sets are found.
        result = self.cl.findVolumeSet(VOLUME_NAME1)
        self.assertIsNone(result)

        self.printFooter('add_remove_volume_in_volume_set')

    def test_8_get_volume_sets(self):
        self.printHeader('get_volume_sets')

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1")
        self.cl.createVolumeSet(VOLUME_SET_NAME2, domain=self.DOMAIN)

        sets = self.cl.getVolumeSets()
        self.assertIsNotNone(sets)
        set_names = [vset['name'] for vset in sets['members']]

        self.assertIn(VOLUME_SET_NAME1, set_names)
        self.assertIn(VOLUME_SET_NAME2, set_names)

        self.printFooter('get_volume_sets')

    def test_8_find_all_volume_sets(self):
        self.printHeader('find_all_volume_sets')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, 1024, optional)
        optional = {'comment': 'test volume 3', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME3, CPG_NAME1, 1024, optional)

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1")
        self.cl.createVolumeSet(VOLUME_SET_NAME2,
                                domain=self.DOMAIN,
                                comment="Unit test volume set 2",
                                setmembers=[VOLUME_NAME1])
        self.cl.createVolumeSet(VOLUME_SET_NAME3,
                                domain=self.DOMAIN,
                                comment="Unit test volume set 3",
                                setmembers=[VOLUME_NAME1, VOLUME_NAME2])

        sets = self.cl.findAllVolumeSets(VOLUME_NAME1)
        self.assertIsNotNone(sets)
        set_names = [vset['name'] for vset in sets]

        self.assertIn(VOLUME_SET_NAME2, set_names)
        self.assertIn(VOLUME_SET_NAME3, set_names)
        self.assertNotIn(VOLUME_SET_NAME1, set_names)

        sets = self.cl.findAllVolumeSets(VOLUME_NAME3)
        expected = []
        self.assertEqual(sets, expected)

        self.printFooter('find_all_volume_sets')

    def test_8_find_volume_set(self):
        self.printHeader('find_volume_set')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, 1024, optional)
        optional = {'comment': 'test volume 3', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME3, CPG_NAME1, 1024, optional)

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1")
        self.cl.createVolumeSet(VOLUME_SET_NAME2,
                                domain=self.DOMAIN,
                                comment="Unit test volume set 2",
                                setmembers=[VOLUME_NAME1])
        self.cl.createVolumeSet(VOLUME_SET_NAME3,
                                domain=self.DOMAIN,
                                comment="Unit test volume set 3",
                                setmembers=[VOLUME_NAME1, VOLUME_NAME2])

        result = self.cl.findVolumeSet(VOLUME_NAME1)
        self.assertEqual(result, VOLUME_SET_NAME2)

        # Check that None is returned if no volume sets are found.
        result = self.cl.findVolumeSet(VOLUME_NAME3)
        self.assertIsNone(result)

        self.printFooter('find_volumet_set')

    def test_9_del_volume_set_empty(self):
        self.printHeader('del_volume_set_empty')

        self.cl.createVolumeSet(VOLUME_SET_NAME2, domain=self.DOMAIN)
        self.cl.deleteVolumeSet(VOLUME_SET_NAME2)

        self.printFooter('del_volume_set_empty')

    def test_9_del_volume_set_with_volumes(self):
        self.printHeader('delete_volume_set_with_volumes')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)

        members = [VOLUME_NAME1, VOLUME_NAME2]
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1",
                                setmembers=members)

        self.cl.deleteVolumeSet(VOLUME_SET_NAME1)

        self.printFooter('delete_volume_set_with_volumes')

    def test_10_modify_volume_set_change_name(self):
        self.printHeader('modify_volume_set_change_name')

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="First")
        self.cl.modifyVolumeSet(VOLUME_SET_NAME1,
                                newName=VOLUME_SET_NAME2)
        vset = self.cl.getVolumeSet(VOLUME_SET_NAME2)
        self.assertEqual("First", vset['comment'])

        self.printFooter('modify_volume_set_change_name')

    def test_10_modify_volume_set_change_comment(self):
        self.printHeader('modify_volume_set_change_comment')

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="First")
        self.cl.modifyVolumeSet(VOLUME_SET_NAME1,
                                comment="Second")
        vset = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        self.assertEqual("Second", vset['comment'])

        self.printFooter('modify_volume_set_change_comment')

    def test_10_modify_volume_set_change_flash_cache(self):
        self.printHeader('modify_volume_set_change_flash_cache')

        try:
            self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                    comment="First")
            self.cl.modifyVolumeSet(
                VOLUME_SET_NAME1,
                flashCachePolicy=self.cl.FLASH_CACHE_ENABLED)
            vset = self.cl.getVolumeSet(VOLUME_SET_NAME1)
            self.assertEqual(self.cl.FLASH_CACHE_ENABLED,
                             vset['flashCachePolicy'])

            self.cl.modifyVolumeSet(
                VOLUME_SET_NAME1,
                flashCachePolicy=self.cl.FLASH_CACHE_DISABLED)
            vset = self.cl.getVolumeSet(VOLUME_SET_NAME1)
            self.assertEqual(self.cl.FLASH_CACHE_DISABLED,
                             vset['flashCachePolicy'])
        except exceptions.HTTPBadRequest:
            # means we are on a server that doesn't support FlashCachePolicy
            # pre 3.2.1 MU2
            pass
        except exceptions.HTTPNotFound as e:
            # Pass if server doesn't have flash cache
            # Not found (HTTP 404) 285 - Flash cache does not exist
            if e.get_code() == 285:
                pass
            else:
                raise

        self.printFooter('modify_volume_set_change_flash_cache')

    def test_10_modify_volume_set_add_members_to_empty(self):
        self.printHeader('modify_volume_set_add_members_to_empty')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)

        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1")

        members = [VOLUME_NAME1, VOLUME_NAME2]
        self.cl.modifyVolumeSet(VOLUME_SET_NAME1, self.cl.SET_MEM_ADD,
                                setmembers=members)

        resp = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        print(resp)
        self.assertTrue(VOLUME_NAME1 in resp['setmembers'])
        self.assertTrue(VOLUME_NAME2 in resp['setmembers'])

        self.printFooter('modify_volume_set_add_members_to_empty')

    def test_10_modify_volume_set_add_members(self):
        self.printHeader('modify_volume_set_add_members')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)

        members = [VOLUME_NAME1]
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                setmembers=members,
                                comment="Unit test volume set 1")

        members = [VOLUME_NAME2]
        self.cl.modifyVolumeSet(VOLUME_SET_NAME1, self.cl.SET_MEM_ADD,
                                setmembers=members)

        resp = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        print(resp)
        self.assertTrue(VOLUME_NAME1 in resp['setmembers'])
        self.assertTrue(VOLUME_NAME2 in resp['setmembers'])

        self.printFooter('modify_volume_set_add_members')

    def test_10_modify_volume_set_del_members(self):
        self.printHeader('modify_volume_del_members')

        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)
        members = [VOLUME_NAME1, VOLUME_NAME2]
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1",
                                setmembers=members)

        members = [VOLUME_NAME1]
        self.cl.modifyVolumeSet(VOLUME_SET_NAME1,
                                action=self.cl.SET_MEM_REMOVE,
                                setmembers=members)

        resp = self.cl.getVolumeSet(VOLUME_SET_NAME1)
        self.assertIsNotNone(resp)
        resp_members = resp['setmembers']
        self.assertNotIn(VOLUME_NAME1, resp_members)
        self.assertIn(VOLUME_NAME2, resp_members)

        self.printFooter('modify_volume_del_members')

    def _create_vv_sets(self):
        optional = {'comment': 'test volume 1', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        optional = {'comment': 'test volume 2', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)
        members = [VOLUME_NAME1, VOLUME_NAME2]
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=self.DOMAIN,
                                comment="Unit test volume set 1",
                                setmembers=members)

    def test_11_add_qos(self):
        self.printHeader('add_qos')

        self._create_vv_sets()
        qos = {'bwMinGoalKB': 1024,
               'bwMaxLimitKB': 1024}

        self.cl.createQoSRules(VOLUME_SET_NAME1, qos)
        rule = self.cl.queryQoSRule(VOLUME_SET_NAME1)

        self.assertIsNotNone(rule)
        self.assertEquals(rule['bwMinGoalKB'], qos['bwMinGoalKB'])
        self.assertEquals(rule['bwMaxLimitKB'], qos['bwMaxLimitKB'])

        self.printFooter('add_qos')

    def test_12_modify_qos(self):
        self.printHeader('modify_qos')

        self._create_vv_sets()
        qos_before = {'bwMinGoalKB': 1024,
                      'bwMaxLimitKB': 1024}
        qos_after = {'bwMinGoalKB': 1024,
                     'bwMaxLimitKB': 2048}

        self.cl.createQoSRules(VOLUME_SET_NAME1, qos_before)
        self.cl.modifyQoSRules(VOLUME_SET_NAME1, qos_after)
        rule = self.cl.queryQoSRule(VOLUME_SET_NAME1)

        self.assertIsNotNone(rule)
        self.assertEquals(rule['bwMinGoalKB'], qos_after['bwMinGoalKB'])
        self.assertEquals(rule['bwMaxLimitKB'], qos_after['bwMaxLimitKB'])

        self.printFooter('modify_qos')

    def test_13_delete_qos(self):
        self.printHeader('delete_qos')

        self._create_vv_sets()
        self.cl.createVolumeSet(VOLUME_SET_NAME2)

        qos1 = {'bwMinGoalKB': 1024,
                'bwMaxLimitKB': 1024}
        qos2 = {'bwMinGoalKB': 512,
                'bwMaxLimitKB': 2048}

        self.cl.createQoSRules(VOLUME_SET_NAME1, qos1)
        self.cl.createQoSRules(VOLUME_SET_NAME2, qos2)
        all_qos = self.cl.queryQoSRules()
        self.assertGreaterEqual(all_qos['total'], 2)
        self.assertIn(VOLUME_SET_NAME1,
                      [qos['name'] for qos in all_qos['members']])
        self.assertIn(VOLUME_SET_NAME2,
                      [qos['name'] for qos in all_qos['members']])

        self.cl.deleteQoSRules(VOLUME_SET_NAME1)
        all_qos = self.cl.queryQoSRules()

        self.assertIsNotNone(all_qos)
        self.assertNotIn(VOLUME_SET_NAME1,
                         [qos['name'] for qos in all_qos['members']])
        self.assertIn(VOLUME_SET_NAME2,
                      [qos['name'] for qos in all_qos['members']])

        self.printFooter('delete_qos')

    def test_14_modify_volume_rename(self):
        self.printHeader('modify volume')

        # add one
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        volumeMod = {'newName': VOLUME_NAME2}
        self.cl.modifyVolume(VOLUME_NAME1, volumeMod)
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        self.assertIsNotNone(vol2)
        self.assertEqual(vol2['comment'], optional['comment'])

        self.printFooter('modify volume')

    def test_15_set_volume_metadata(self):
        self.printHeader('set volume metadata')

        optional = {'comment': 'test volume', 'tpvv': True}
        expected_value = 'test_val'
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.setVolumeMetaData(VOLUME_NAME1, 'test_key', expected_value)
        result = self.cl.getVolumeMetaData(VOLUME_NAME1, 'test_key')
        self.assertEqual(result['value'], expected_value)

        self.printFooter('set volume metadata')

    def test_15_set_bad_volume_metadata(self):
        self.printHeader('set bad volume metadata')

        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.setVolumeMetaData,
                          'Fake_Volume',
                          'test_key',
                          'test_val')

        self.printFooter('set bad volume metadata')

    def test_15_set_volume_metadata_existing_key(self):
        self.printHeader('set volume metadata existing key')

        optional = {'comment': 'test volume', 'tpvv': True}
        expected = 'new_test_val'
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.setVolumeMetaData(VOLUME_NAME1, 'test_key', 'test_val')
        self.cl.setVolumeMetaData(VOLUME_NAME1, 'test_key', 'new_test_val')
        contents = self.cl.getVolumeMetaData(VOLUME_NAME1, 'test_key')
        self.assertEqual(contents['value'], expected)

        self.printFooter('set volume metadata existing key')

    def test_15_set_volume_metadata_invalid_length(self):
        self.printHeader('set volume metadata invalid length')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)

        # Some backends have a key limit of 31 characters while and other
        # are larger
        self.assertRaises(exceptions.HTTPBadRequest,
                          self.cl.setVolumeMetaData,
                          VOLUME_NAME1,
                          'this_key_will_cause_an_exception ' 'x' * 256,
                          'test_val')

        self.printFooter('set volume metadata invalid length')

    def test_15_set_volume_metadata_invalid_data(self):
        self.printHeader('set volume metadata invalid data')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.assertRaises(exceptions.HTTPBadRequest,
                          self.cl.setVolumeMetaData,
                          VOLUME_NAME1,
                          None,
                          'test_val')

        self.printFooter('set volume metadata invalid data')

    def test_16_get_volume_metadata(self):
        self.printHeader('get volume metadata')

        optional = {'comment': 'test volume', 'tpvv': True}
        expected_value = 'test_val'
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.setVolumeMetaData(VOLUME_NAME1, 'test_key', expected_value)
        result = self.cl.getVolumeMetaData(VOLUME_NAME1, 'test_key')
        self.assertEqual(expected_value, result['value'])

        self.printFooter('get volume metadata')

    def test_16_get_volume_metadata_missing_volume(self):
        self.printHeader('get volume metadata missing volume')

        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.getVolumeMetaData,
                          'Fake_Volume',
                          'bad_key')

        self.printFooter('get volume metadata missing volume')

    def test_16_get_volume_metadata_missing_key(self):
        self.printHeader('get volume metadata missing key')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.getVolumeMetaData,
                          VOLUME_NAME1,
                          'bad_key')

        self.printFooter('get volume metadata missing key')

    def test_16_get_volume_metadata_invalid_input(self):
        self.printHeader('get volume metadata invalid input')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.assertRaises(exceptions.HTTPBadRequest,
                          self.cl.getVolumeMetaData,
                          VOLUME_NAME1,
                          '&')

        self.printFooter('get volume metadata invalid input')

    def test_17_get_all_volume_metadata(self):
        self.printHeader('get all volume metadata')

        # Keys present in metadata
        optional = {'comment': 'test volume', 'tpvv': True}
        expected_value_1 = 'test_val'
        expected_value_2 = 'test_val2'
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.setVolumeMetaData(VOLUME_NAME1,
                                  'test_key_1',
                                  expected_value_1)
        self.cl.setVolumeMetaData(VOLUME_NAME1,
                                  'test_key_2',
                                  expected_value_2)
        result = self.cl.getAllVolumeMetaData(VOLUME_NAME1)

        # Key- Value pairs are unordered
        for member in result['members']:
            if member['key'] == 'test_key_1':
                self.assertEqual(expected_value_1, member['value'])
            elif member['key'] == 'test_key_2':
                self.assertEqual(expected_value_2, member['value'])
            else:
                raise Exception("Unexpected member %s" % member)

        # No keys present in metadata
        optional = {'comment': 'test volume', 'tpvv': True}
        expected_value = {'total': 0, 'members': []}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, 1024, optional)
        result = self.cl.getAllVolumeMetaData(VOLUME_NAME2)
        self.assertEqual(expected_value, result)

        self.printFooter('get all volume metadata')

    def test_17_get_all_volume_metadata_missing_volume(self):
        self.printHeader('get all volume metadata missing volume')

        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.getAllVolumeMetaData,
                          'Fake_Volume')

        self.printFooter('get all volume metadata missing volume')

    def test_18_remove_volume_metadata(self):
        self.printHeader('remove volume metadata')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.setVolumeMetaData(VOLUME_NAME1, 'test_key', 'test_val')
        self.cl.removeVolumeMetaData(VOLUME_NAME1, 'test_key')
        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.getVolumeMetaData,
                          VOLUME_NAME1,
                          'test_key')

        self.printFooter('remove volume metadata')

    def test_18_remove_volume_metadata_missing_volume(self):
        self.printHeader('remove volume metadata missing volume')

        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.removeVolumeMetaData,
                          'Fake_Volume',
                          'test_key')

        self.printFooter('remove volume metadata missing volume')

    def test_18_remove_volume_metadata_missing_key(self):
        self.printHeader('remove volume metadata missing key')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.assertRaises(exceptions.HTTPNotFound,
                          self.cl.removeVolumeMetaData,
                          VOLUME_NAME1,
                          'test_key')

        self.printFooter('remove volume metadata missing key')

    def test_18_remove_volume_metadata_invalid_input(self):
        self.printHeader('remove volume metadata invalid input')

        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.assertRaises(exceptions.HTTPBadRequest,
                          self.cl.removeVolumeMetaData,
                          VOLUME_NAME1,
                          '&')

        self.printFooter('remove volume metadata invalid input')

    def test_19_find_volume_metadata(self):
        self.printHeader('find volume metadata')

        # Volume should be found
        optional = {'comment': 'test volume', 'tpvv': True}
        expected = True
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.setVolumeMetaData(VOLUME_NAME1, 'test_key', 'test_val')
        result = self.cl.findVolumeMetaData(VOLUME_NAME1,
                                            'test_key',
                                            'test_val')
        self.assertEqual(result, expected)

        # Volume should not be found
        optional = {'comment': 'test volume', 'tpvv': True}
        expected = False
        result = self.cl.findVolumeMetaData(VOLUME_NAME1,
                                            'bad_key',
                                            'test_val')
        self.assertEqual(result, expected)

        self.printFooter('find volume metadata')

    def test_19_find_volume_metadata_missing_volume(self):
        self.printHeader('find volume metadata missing volume')

        expected = False
        result = self.cl.findVolumeMetaData('Fake_Volume',
                                            'test_key',
                                            'test_val')
        self.assertEqual(result, expected)

        self.printFooter('find volume metadata missing volume')

    def test_20_create_vvset_snapshot_no_optional(self):
        self.printHeader('create_vvset_snapshot_no_optional')

        # create volume to add to volume set
        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # create volume set and add a volume to it
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=DOMAIN,
                                setmembers=[VOLUME_NAME1])

        # @count@ is needed by 3PAR to create volume set snapshots. will
        # create SNAP_NAME1-0 format
        self.cl.createSnapshotOfVolumeSet(SNAP_NAME1 + "-@count@",
                                          VOLUME_SET_NAME1)

        # assert snapshot was created
        snap = SNAP_NAME1 + "-0"
        snapshot = self.cl.getVolume(snap)
        self.assertEqual(VOLUME_NAME1, snapshot['copyOf'])

        # cleanup volume snapshot and volume set
        self.cl.deleteVolume(snap)
        self.cl.deleteVolumeSet(VOLUME_SET_NAME1)

        self.printFooter('create_vvset_snapshot_no_optional')

    def test_20_create_vvset_snapshot(self):
        self.printHeader('create_vvset_snapshot')

        # create volume to add to volume set
        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # create volume set and add a volume to it
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=DOMAIN,
                                setmembers=[VOLUME_NAME1])

        # @count@ is needed by 3PAR to create volume set snapshots. will
        # create SNAP_NAME1-0 format
        optional = {'expirationHours': 300}
        self.cl.createSnapshotOfVolumeSet(SNAP_NAME1 + "-@count@",
                                          VOLUME_SET_NAME1, optional)

        # assert snapshot was created
        snap = SNAP_NAME1 + "-0"
        snapshot = self.cl.getVolume(snap)
        self.assertEqual(VOLUME_NAME1, snapshot['copyOf'])

        # cleanup volume snapshot and volume set
        self.cl.deleteVolume(snap)
        self.cl.deleteVolumeSet(VOLUME_SET_NAME1)

        self.printFooter('create_vvset_snapshot')

    def test_20_create_vvset_snapshot_badParams(self):
        self.printHeader('create_vvset_snapshot_badParams')

        # add one
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=DOMAIN)

        optional = {'Bad': True, 'expirationHours': 300}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createSnapshotOfVolumeSet,
            SNAP_NAME1,
            VOLUME_SET_NAME1,
            optional
        )

        self.printFooter('create_vvset_snapshot_badParams')

    def test_20_create_vvset_snapshot_nonExistVolumeSet(self):
        self.printHeader('create_vvset_snapshot_nonExistVolume')

        # add one
        name = 'UnitTestVvsetSnapshot'
        volSetName = 'NonExistVolumeSet'
        optional = {'comment': 'test vvset snapshot',
                    'readOnly': True, 'expirationHours': 300}
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.createSnapshotOfVolumeSet,
            name,
            volSetName,
            optional
        )

        self.printFooter('create_vvset_snapshot_nonExistVolume')

    def test_20_create_vvset_emptyVolumeSet(self):
        self.printHeader('test_20_create_vvset_emptyVolumeSet')

        name = 'UnitTestVvsetSnapshot'
        self.cl.createVolumeSet(VOLUME_SET_NAME1, domain=DOMAIN)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.createSnapshotOfVolumeSet,
            name,
            VOLUME_SET_NAME1
        )

        self.cl.deleteVolumeSet(VOLUME_SET_NAME1)

        self.printFooter('test_20_create_vvset_emptyVolumeSet')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_create_remote_copy_group(self):
        self.printHeader('create_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        self.printFooter('create_remote_copy_group')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_delete_remote_copy_group(self):
        self.printHeader('delete_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Delete remote copy group
        self.cl.removeRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getRemoteCopyGroup,
            REMOTE_COPY_GROUP_NAME1
        )

        self.printFooter('create_delete_copy_group')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_modify_remote_copy_group(self):
        self.printHeader('modify_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        REMOTE_COPY_TARGETS[0]['syncPeriod'] = 300
        self.cl.modifyRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      {'targets': REMOTE_COPY_TARGETS})
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(300, targets[0]['syncPeriod'])

        self.printFooter('modify_remote_copy_group')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_add_volume_to_remote_copy_group(self):
        self.printHeader('add_volume_to_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        self.printFooter('add_volume_to_remote_copy_group')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_add_volume_to_remote_copy_group_nonExistVolume(self):
        self.printHeader('add_volume_to_remote_copy_group_nonExistVolume')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Add non existent volume to remote copy group
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.addVolumeToRemoteCopyGroup,
            REMOTE_COPY_GROUP_NAME1,
            'BAD_VOLUME_NAME',
            REMOTE_COPY_TARGETS
        )

        self.printFooter('add_volume_to_remote_copy_group_nonExistVolume')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_remove_volume_from_remote_copy_group(self):
        self.printHeader('remove_volume_from_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        # Remove volume from remote copy group
        self.cl.removeVolumeFromRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                                RC_VOLUME_NAME,
                                                useHttpDelete=False)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual([], volumes)

        self.printFooter('remove_volume_from_remote_copy_group')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_start_remote_copy(self):
        self.printHeader('start_remote_copy')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        self.printFooter('start_remote_copy')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_stop_remote_copy(self):
        self.printHeader('stop_remote_copy')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        # Stop remote copy for the group
        self.cl.stopRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STOPPED, targets[0]['state'])

        self.printFooter('stop_remote_copy')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_synchronize_remote_copy_group(self):
        self.printHeader('synchronize_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        # Synchronize the remote copy group
        self.cl.synchronizeRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        assert targets[0]['groupLastSyncTime'] is not None

        self.printFooter('synchronize_remote_copy_group')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_21_failover_remote_copy_group(self):
        self.printHeader('failover_remote_copy_group')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        # Failover remote copy group
        self.cl.recoverRemoteCopyGroupFromDisaster(REMOTE_COPY_GROUP_NAME1,
                                                   FAILOVER_GROUP)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(True, resp['roleReversed'])

        self.printFooter('failover_remote_copy_group')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_create_remote_copy_group(self):
        self.printHeader('create_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Check remote copy group on the secondary array
        info = self.cl.getStorageSystemInfo()
        client_id = str(info['id'])
        target_rcg_name = REMOTE_COPY_GROUP_NAME1 + ".r" + client_id
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        self.assertEqual(target_rcg_name, resp['name'])

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_delete_remote_copy_group(self):
        self.printHeader('delete_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Check remote copy group on the secondary array
        info = self.cl.getStorageSystemInfo()
        client_id = str(info['id'])
        target_rcg_name = REMOTE_COPY_GROUP_NAME1 + ".r" + client_id
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        self.assertEqual(target_rcg_name, resp['name'])

        # Delete remote copy group
        self.cl.removeRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getRemoteCopyGroup,
            REMOTE_COPY_GROUP_NAME1
        )

        # Check remote copy does not exist on target array
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.secondary_cl.getRemoteCopyGroup,
            REMOTE_COPY_GROUP_NAME1
        )

        self.printFooter('create_delete_copy_group')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_modify_remote_copy_group(self):
        self.printHeader('modify_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Check remote copy group on the secondary array
        info = self.cl.getStorageSystemInfo()
        client_id = str(info['id'])
        target_rcg_name = REMOTE_COPY_GROUP_NAME1 + ".r" + client_id
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        self.assertEqual(target_rcg_name, resp['name'])

        # Modify the remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'syncPeriod': 300}]
        self.cl.modifyRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      {'targets': targets})
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(300, targets[0]['syncPeriod'])

        # Check modification on target array
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        targets = resp['targets']
        self.assertEqual(300, targets[0]['syncPeriod'])

        self.printFooter('modify_remote_copy_group')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_add_volume_to_remote_copy_group(self):
        self.printHeader('add_volume_to_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Check remote copy group on the secondary array
        info = self.cl.getStorageSystemInfo()
        client_id = str(info['id'])
        target_rcg_name = REMOTE_COPY_GROUP_NAME1 + ".r" + client_id
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        self.assertEqual(target_rcg_name, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE,
                             optional)

        # Add volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        optional = {'volumeAutoCreation': True}
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           targets,
                                           optional=optional)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['localVolumeName'])
        remote_volumes = volumes[0]['remoteVolumes']
        self.assertEqual(RC_VOLUME_NAME, remote_volumes[0]['remoteVolumeName'])

        self.printFooter('add_volume_to_remote_copy_group')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_add_volume_to_remote_copy_group_nonExistVolume(self):
        self.printHeader('add_volume_to_remote_copy_group_nonExistVolume')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Check remote copy group on the secondary array
        info = self.cl.getStorageSystemInfo()
        client_id = str(info['id'])
        target_rcg_name = REMOTE_COPY_GROUP_NAME1 + ".r" + client_id
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        self.assertEqual(target_rcg_name, resp['name'])

        # Add non existent volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.addVolumeToRemoteCopyGroup,
            REMOTE_COPY_GROUP_NAME1,
            'BAD_VOLUME_NAME',
            targets
        )

        self.printFooter('add_volume_to_remote_copy_group_nonExistVolume')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_remove_volume_from_remote_copy_group(self):
        self.printHeader('remove_volume_from_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE,
                             optional)

        # Add volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        optional = {'volumeAutoCreation': True}
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           targets,
                                           optional=optional)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['localVolumeName'])
        remote_volumes = volumes[0]['remoteVolumes']
        self.assertEqual(RC_VOLUME_NAME, remote_volumes[0]['remoteVolumeName'])

        # Remove volume from remote copy group
        self.cl.removeVolumeFromRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                                RC_VOLUME_NAME,
                                                removeFromTarget=True,
                                                useHttpDelete=False)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual([], volumes)

        # Check volume does not exist on target array
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.secondary_cl.getVolume,
            RC_VOLUME_NAME
        )

        self.printFooter('remove_volume_from_remote_copy_group')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_start_remote_copy(self):
        self.printHeader('start_remote_copy')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE,
                             optional)

        # Add volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        optional = {'volumeAutoCreation': True}
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           targets,
                                           optional=optional)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['localVolumeName'])
        remote_volumes = volumes[0]['remoteVolumes']
        self.assertEqual(RC_VOLUME_NAME, remote_volumes[0]['remoteVolumeName'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        self.printFooter('start_remote_copy')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_stop_remote_copy(self):
        self.printHeader('start_remote_copy')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE,
                             optional)

        # Add volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        optional = {'volumeAutoCreation': True}
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           targets,
                                           optional=optional)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['localVolumeName'])
        remote_volumes = volumes[0]['remoteVolumes']
        self.assertEqual(RC_VOLUME_NAME, remote_volumes[0]['remoteVolumeName'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        # Stop remote copy for the group
        self.cl.stopRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STOPPED, targets[0]['state'])

        self.printFooter('start_remote_copy')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_synchronize_remote_copy_group(self):
        self.printHeader('synchronize_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE,
                             optional)

        # Add volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        optional = {'volumeAutoCreation': True}
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           targets,
                                           optional=optional)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['localVolumeName'])
        remote_volumes = volumes[0]['remoteVolumes']
        self.assertEqual(RC_VOLUME_NAME, remote_volumes[0]['remoteVolumeName'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        # Synchronize the remote copy group
        self.cl.synchronizeRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        assert targets[0]['groupLastSyncTime'] is not None

        self.printFooter('synchronize_remote_copy_group')

    @unittest.skipIf(no_remote_copy(), SKIP_FLASK_RCOPY_MESSAGE)
    def test_22_failover_remote_copy_group(self):
        self.printHeader('failover_remote_copy_group')

        # Create empty remote copy group
        targets = [{"targetName": self.secondary_target_name,
                    "mode": 2,
                    "userCPG": CPG_NAME1,
                    "snapCPG": CPG_NAME1}]
        optional = {'localSnapCPG': CPG_NAME1,
                    'localUserCPG': CPG_NAME1,
                    'domain': DOMAIN}
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      targets,
                                      optional=optional)

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE,
                             optional)

        # Add volume to remote copy group
        targets = [{'targetName': self.secondary_target_name,
                    'secVolumeName': RC_VOLUME_NAME}]
        optional = {'volumeAutoCreation': True}
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           targets,
                                           optional=optional)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['localVolumeName'])
        remote_volumes = volumes[0]['remoteVolumes']
        self.assertEqual(RC_VOLUME_NAME, remote_volumes[0]['remoteVolumeName'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        # Stop remote copy for the group
        self.cl.stopRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STOPPED, targets[0]['state'])

        # Failover remote copy group
        info = self.cl.getStorageSystemInfo()
        client_id = str(info['id'])
        target_rcg_name = REMOTE_COPY_GROUP_NAME1 + ".r" + client_id
        self.secondary_cl.recoverRemoteCopyGroupFromDisaster(
            target_rcg_name, FAILOVER_GROUP)
        resp = self.secondary_cl.getRemoteCopyGroup(target_rcg_name)
        targets = resp['targets']
        self.assertEqual(True, targets[0]['roleReversed'])

        # Restore the remote copy group
        self.secondary_cl.recoverRemoteCopyGroupFromDisaster(
            target_rcg_name, RESTORE_GROUP)
        # Let the restore take affect
        time.sleep(10)

        self.printFooter('failover_remote_copy_group')

    def test_23_get_volume_snapshots(self):
        # Create volume and snaphot it
        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        self.cl.createSnapshot(SNAP_NAME1, VOLUME_NAME1)
        self.cl.createSnapshot(SNAP_NAME2, VOLUME_NAME1)

        # Get the volumes snapshots
        live_test = is_live_test()
        snapshots = self.cl.getVolumeSnapshots(VOLUME_NAME1, live_test)

        # If the volume has snapshots, their names will be returned as
        # a list
        self.assertEqual([SNAP_NAME1, SNAP_NAME2], snapshots)

        # Test where volume does not exist
        snapshots = self.cl.getVolumeSnapshots("BAD_VOL")
        # An empty list is returned if the volume does not exist
        self.assertEqual([], snapshots)

    def test_24_set_qos(self):
        self.printHeader('set_qos')
        self.cl.createVolumeSet(VOLUME_SET_NAME4,
                                comment="Unit test volume set 4")

        self.assertRaises(
            exceptions.SetQOSRuleException,
            self.cl.setQOSRule,
            VOLUME_SET_NAME4)

        max_io = 300
        max_bw = 1024
        self.cl.setQOSRule(VOLUME_SET_NAME4, max_io, max_bw)
        self.cl.setQOSRule(VOLUME_SET_NAME4, max_io)
        self.cl.setQOSRule(VOLUME_SET_NAME4, max_bw)

        self.printFooter('set_qos')

    def test_25_promote_virtual_copy(self):
        self.printHeader('promote_virtual_copy')

        optional = {'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        # add one
        self.cl.createSnapshot(SNAP_NAME1, VOLUME_NAME1)
        # no API to get and check

        resp = self.cl.promoteVirtualCopy(SNAP_NAME1)
        self.assertIsNotNone(resp['taskid'])

        self.printFooter('promote_virtual_copy')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_25_promote_virtual_copy_on_replicated_volume(self):
        self.printHeader('promote_virtual_copy_on_replicated_volume')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        self.cl.createSnapshot(SNAP_NAME1, RC_VOLUME_NAME)

        # Stop remote copy for the group
        self.cl.stopRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STOPPED, targets[0]['state'])

        optional = {'allowRemoteCopyParent': True}
        resp = self.cl.promoteVirtualCopy(SNAP_NAME1, optional)
        self.assertIsNotNone(resp['taskid'])

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        self.printFooter('promote_virtual_copy_on_replicated_volume')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_25_promote_virtual_copy_with_bad_param(self):
        self.printHeader('promote_virtual_copy_with_bad_param')

        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE)
        # add one
        self.cl.createSnapshot(SNAP_NAME1, VOLUME_NAME1)
        # no API to get and check

        optional = {'online': True,
                    'allowRemoteCopyParent': True,
                    'priority': 1}
        self.assertRaises(
            exceptions.HTTPConflict,
            self.cl.promoteVirtualCopy,
            SNAP_NAME1,
            optional
        )

        self.printFooter('promote_virtual_copy_with_bad_param')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test_25_promote_vcopy_on_rep_vol_with_bad_param(self):
        self.printHeader('promote_vcopy_on_rep_vol_with_bad_param')

        # Create empty remote copy group
        self.cl.createRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                      REMOTE_COPY_TARGETS,
                                      optional={"domain": DOMAIN})

        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(REMOTE_COPY_GROUP_NAME1, resp['name'])

        # Create volume
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(RC_VOLUME_NAME, CPG_NAME1, SIZE, optional)

        # Add volume to remote copy group
        self.cl.addVolumeToRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1,
                                           RC_VOLUME_NAME,
                                           REMOTE_COPY_TARGETS)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        volumes = resp['volumes']
        self.assertEqual(RC_VOLUME_NAME, volumes[0]['name'])

        self.cl.createSnapshot(SNAP_NAME1, RC_VOLUME_NAME)

        # Stop remote copy for the group
        self.cl.stopRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STOPPED, targets[0]['state'])

        self.assertRaises(
            exceptions.HTTPForbidden,
            self.cl.promoteVirtualCopy,
            SNAP_NAME1,
            optional
        )

        # Start remote copy for the group
        self.cl.startRemoteCopy(REMOTE_COPY_GROUP_NAME1)
        resp = self.cl.getRemoteCopyGroup(REMOTE_COPY_GROUP_NAME1)
        targets = resp['targets']
        self.assertEqual(RCOPY_STARTED, targets[0]['state'])

        self.printFooter('promote_vcopy_on_rep_vol_with_bad_param')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test26_admit_rcopy_link(self):
        self.printHeader('admit_rcopy_link_test')
        res = self.cl.admitRemoteCopyLinks(TARGET_NAME,
                                           SOURCE_PORT,
                                           TARGET_PORT)
        self.assertEqual(res, [])
        self.printFooter('admit_rcopy_link_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test27_dismiss_rcopy_link(self):
        self.printHeader('dismiss_rcopy_link_test')
        res = self.cl.dismissRemoteCopyLinks(TARGET_NAME,
                                             SOURCE_PORT,
                                             TARGET_PORT)
        self.assertEqual(res, [])
        self.printFooter('dismiss_rcopy_link_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test28_start_rcopy(self):
        self.printHeader('start_rcopy_test')
        res = self.cl.startrCopy()
        self.assertEqual(res, [])
        self.printFooter('start_rcopy_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test29_admit_rcopy_target(self):
        self.printHeader('admit_rcopy_target_test')
        res = self.cl.admitRemoteCopyTarget(TARGET_NAME,
                                            MODE,
                                            REMOTE_COPY_GROUP_NAME1)
        self.assertEqual(res, [])
        self.printFooter('admit_rcopy_target_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test30_admit_rcopy_target(self):
        self.printHeader('admit_rcopy_target_test')
        res = self.cl.admitRemoteCopyTarget(TARGET_NAME,
                                            MODE,
                                            REMOTE_COPY_GROUP_NAME1,
                                            VOLUME_PAIR_LIST)
        self.assertEqual(res, [])
        self.printFooter('admit_rcopy_target_test')

    # TODO: Fix this later
    # @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    # def test31_dismiss_rcopy_target(self):
    #    self.printHeader('dismiss_rcopy_target_test')
    #    res = self.cl.dismissRemoteCopyTarget(TARGET_NAME,
    #                                          REMOTE_COPY_GROUP_NAME1)
    #    self.assertEqual(res, [])
    #    self.printFooter('dismiss_rcopy_target_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test32_create_schedule(self):
        self.printHeader('create_schedule_test')
        cmd = "createsv -ro snap-" + VOLUME_NAME1 + " " + VOLUME_NAME1
        res = self.cl.createSchedule(SCHEDULE_NAME1, cmd, 'hourly')
        self.assertEqual(res, None)
        self.printFooter('create_schedule_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test33_delete_schedule(self):
        self.printHeader('delete_schedule_test')
        res = self.cl.deleteSchedule(SCHEDULE_NAME1)
        self.assertEqual(res, None)
        self.printFooter('delete_schedule_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test34_modify_schedule(self):
        self.printHeader('modify_schedule_test')
        res = self.cl.modifySchedule(SCHEDULE_NAME1,
                                     {'newName': SCHEDULE_NAME2})
        self.assertEqual(res, None)
        self.printFooter('modify_schedule_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test35_suspend_schedule(self):
        self.printHeader('suspend_schedule_test')
        res = self.cl.suspendSchedule(SCHEDULE_NAME1)
        self.assertEqual(res, None)
        self.printFooter('suspend_schedule_test')

    @unittest.skipIf(is_live_test(), SKIP_RCOPY_MESSAGE)
    def test36_resume_schedule(self):
        self.printHeader('resume_schedule_test')
        res = self.cl.resumeSchedule(SCHEDULE_NAME1)
        self.assertEqual(res, None)
        self.printFooter('resume_schedule_test')

    def test37_create_volume_with_primera_support_with_no_option(self):
        self.printHeader('create_volume')
        self.cl.primera_supported = True
        # add volume with no options specified,
        # it should create bydefault tpvv volume
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE)
        # check
        vol1 = self.cl.getVolume(VOLUME_NAME1)
        self.assertIsNotNone(vol1)
        volName = vol1['name']
        self.assertEqual(VOLUME_NAME1, volName)
        self.printFooter('create_volume')

    def test38_create_volume_with_primera_support_with_option(self):
        self.printHeader('create_volume')
        self.cl.primera_supported = True
        # add one
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # check
        vol1 = self.cl.getVolume(VOLUME_NAME1)
        self.assertIsNotNone(vol1)
        volName = vol1['name']
        self.assertEqual(VOLUME_NAME1, volName)

        # add another compressed volume
        optional = {'comment': 'test volume2', 'compression': True,
                    'tdvv': True}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME2, 16384, optional)

        # check
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        self.assertIsNotNone(vol2)

        volName = vol2['name']
        comment = vol2['comment']
        reduced = vol2['reduce']

        self.assertEqual(VOLUME_NAME2, volName)
        self.assertEqual("test volume2", comment)
        self.assertEqual(True, reduced)

    def test38_create_volume_with_primera_support_with_option_None(self):
        self.printHeader('create_volume')
        self.cl.primera_supported = True
        # add one
        optional = {'comment': 'test volume', 'tpvv': None,
                    'compression': True, 'tdvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 16384, optional)
        # check
        vol1 = self.cl.getVolume(VOLUME_NAME1)
        self.assertIsNotNone(vol1)
        volName = vol1['name']
        reduced = vol1['reduce']
        comment = vol1['comment']
        self.assertEqual(VOLUME_NAME1, volName)
        self.assertEqual("test volume", comment)
        self.assertEqual(True, reduced)
        # add another one
        optional = {'comment': 'test volume2', 'tpvv': True,
                    'compression': None, 'tdvv': None}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)

        # check
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        self.assertIsNotNone(vol2)
        volName = vol2['name']
        comment = vol2['comment']
        self.assertEqual(VOLUME_NAME2, volName)
        self.assertEqual("test volume2", comment)
        self.printFooter('create_volume')

    def test_39_create_volume_badParams(self):
        self.printHeader('create_volume_badParams')
        self.cl.merlin_supported = True
        optional = {'comment': 'test volume', 'tpvv': "junk"}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            VOLUME_NAME1,
            CPG_NAME1,
            SIZE,
            optional)
        self.printFooter('create_volume_badParams')

    def test_40_create_volume_badParams(self):
        self.printHeader('create_volume_badParams')
        self.cl.primera_supported = True
        optional = {'comment': 'test volume', 'compression': "junk",
                    'tdvv': "junk"}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            VOLUME_NAME1,
            CPG_NAME1,
            SIZE,
            optional)
        self.printFooter('create_volume_badParams')

    def test_41_create_volume_junk_values(self):
        self.printHeader('create_volume_junkParams')
        self.cl.primera_supported = True
        optional = {'comment': 'test volume', 'tpvv': "junk",
                    'compression': "junk"}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            VOLUME_NAME1,
            CPG_NAME1,
            SIZE,
            optional)
        self.printFooter('create_volume_junkParams')

    def test_42_create_volume_junk_compression(self):
        self.printHeader('create_volume_junkParams')
        self.cl.primera_supported = True
        optional = {'comment': 'test volume', 'tpvv': None,
                    'compression': "junk"}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.createVolume,
            VOLUME_NAME1,
            CPG_NAME1,
            SIZE,
            optional)
        self.printFooter('create_volume_junkParams')

    def test_43_create_volume_parameter_absent(self):
        self.printHeader('create_volume_noParams')
        self.cl.primera_supported = True
        optional = {'comment': 'test volume',
                    'compression': False}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        # check
        vol1 = self.cl.getVolume(VOLUME_NAME1)
        self.assertIsNotNone(vol1)
        volName = vol1['name']
        comment = vol1['comment']
        self.assertEqual(VOLUME_NAME1, volName)
        self.assertEqual("test volume", comment)

        # add another one
        optional = {'comment': 'test volume2',
                    'tpvv': False}
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, SIZE, optional)
        # check
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        self.assertIsNotNone(vol2)
        volName = vol2['name']
        comment = vol2['comment']
        self.assertEqual(VOLUME_NAME2, volName)
        self.assertEqual("test volume2", comment)
        self.printFooter('create_volume_noParams')

    def test_44_offline_copy_volume_primera_support(self):
        self.printHeader('copy_volume')
        self.cl.primera_supported = True
        # add one
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024, optional)
        self.cl.createVolume(VOLUME_NAME2, CPG_NAME1, 1024, optional)
        # copy it
        optional1 = {'online': False}
        self.cl.copyVolume(VOLUME_NAME1, VOLUME_NAME2, CPG_NAME1, optional1)
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        volName = vol2['name']
        self.assertEqual(VOLUME_NAME2, volName)
        self.printFooter('copy_volume')

    def test_45_online_copy_volume_primera_support(self):
        self.printHeader('copy_volume')
        self.cl.primera_supported = True
        # TODO: Add support for ssh/stopPhysical copy in mock mode
        if self.unitTest:
            self.printFooter('copy_volume')
            return
        # add one
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # copy it
        # for online copy we need to specify the tpvv/reduce for merlin
        optional = {'online': True, 'tpvv': True}
        self.cl.copyVolume(VOLUME_NAME1, VOLUME_NAME2, CPG_NAME1, optional)
        vol2 = self.cl.getVolume(VOLUME_NAME2)
        volName = vol2['name']
        self.assertEqual(VOLUME_NAME2, volName)
        self.printFooter('copy_volume')

    def test_46_copy_volume_interrupted_primera_support(self):
        self.printHeader('copy_volume')
        self.cl.primera_supported = True
        # TODO: Add support for ssh/stopPhysical copy in mock mode
        if self.unitTest:
            self.printFooter('copy_volume')
            return
        # add one
        optional = {'comment': 'test volume', 'tpvv': True,
                    'snapCPG': CPG_NAME1}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)

        # copy it
        optional = {'online': True, 'tpvv': True}
        self.cl.copyVolume(VOLUME_NAME1, VOLUME_NAME2, CPG_NAME1, optional)
        self.cl.getVolume(VOLUME_NAME2)
        self.cl.stopOnlinePhysicalCopy(VOLUME_NAME2)

        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.getVolume,
            VOLUME_NAME2
        )

        self.printFooter('copy_volume')

    def test_47_create_default_volume(self):
        self.printHeader('create_volume')
        self.cl.primera_supported = True
        # add one
        optional = {'comment': 'test volume', 'tpvv': True,
                    'compression': False}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        # check
        vol1 = self.cl.getVolume(VOLUME_NAME1)
        self.assertIsNotNone(vol1)
        volName = vol1['name']
        self.assertEqual(VOLUME_NAME1, volName)

    def test_48_tune_volume_to_dedup_compressed_on_primera(self):
        self.printHeader('convert_to_deco')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': CONVERT_TO_DECO,
                    'keepVV': "keep_vv",
                    'compression': False}
        self.cl.tuneVolume(VOLUME_NAME1, usr_cpg, optional)
        vol2 = self.cl.getVolume(VOLUME_NAME1)
        self.assertEqual(vol2['tdvv'], True)
        self.assertEqual(vol2['compression'], True)
        self.printFooter('convert_to_deco')

    def test_49_tune_volume_to_full_on_primera(self):
        self.printHeader('convert_to_full')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': FPVV,
                    'keepVV': "keep_vv",
                    'compression': False}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('convert_to_full')

    def test_50_tune_volume_to_dedup_on_primera(self):
        self.printHeader('convert_to_dedup')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': TDVV,
                    'keepVV': "keep_vv",
                    'compression': False}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('convert_to_dedup')

    def test_51_tune_volume_to_thin_compressed_on_primera(self):
        self.printHeader('convert_to_thin_compressed')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': TPVV,
                    'keepVV': "keep_vv",
                    'compression': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('convert_to_thin_compressed')

    def test_52_tune_volume_with_bad_parameter_primera(self):
        self.printHeader('tune_volume_with_bad_param')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'xyz': "UserCPG",
                    'conversionOperation': TPVV,
                    'keepVV': "keep_vv",
                    'compression': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('tune_volume_with_bad_param')

    def test_53_tune_volume_with_invalid_conversion_operation(self):
        self.printHeader('tune_volume_with_invalid_conversion_operation')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': INVALID_PROVISIONING_TYPE,
                    'keepVV': "keep_vv",
                    'compression': True}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('tune_volume_with_invalid_conversion_operation')

    def test_54_tune_volume_with_invalid_compression_value(self):
        self.printHeader('tune_volume_with_invalid_compression_value')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': FPVV,
                    'keepVV': "keep_vv",
                    'compression': "xyz"}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('tune_volume_with_invalid_compression_value')

    def test_55_tune_volume_with_invalid_usercpg_value(self):
        self.printHeader('tune_volume_with_invalid_usercpg_value')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = INVALID_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': TPVV,
                    'keepVV': "keep_vv",
                    'compression': False}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('tune_volume_with_invalid_usercpg_value')

    def test_56_tune_volume_with_exceeded_length_of_keepvv(self):
        self.printHeader('tune_volume_with_exceeded_length_of_keepvv')
        self.cl.primera_supported = True
        self.cl.compression_supported = True
        optional = {'comment': 'test volume', 'tpvv': True}
        self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, SIZE, optional)
        usr_cpg = USR_CPG
        optional = {'userCPG': "UserCPG",
                    'conversionOperation': TPVV,
                    'keepVV': "asdfjslfjsldkjfasdjlksjdflsdjakjsdlkfjsdjdsdlf",
                    'compression': False}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.tuneVolume,
            VOLUME_NAME1,
            usr_cpg,
            optional)
        self.printFooter('tune_volume_with_exceeded_length_of_keepvv')
# testing
# suite = unittest.TestLoader().
#   loadTestsFromTestCase(HPE3ParClientVolumeTestCase)
# unittest.TextTestRunner(verbosity=2).run(suite)
