# -*- coding:utf-8 -*-
"""
Description:
    Transaction Basic Class
Usage:
    from AntShares.Core.Transaction import Transaction
"""

from AntShares.Core.AssetType import AssetType
from AntShares.Core.Blockchain import Blockchain
from AntShares.Core.CoinReference import CoinReference
from AntShares.Core.TransactionOutput import TransactionOutput
from AntShares.Core.TransactionType import TransactionType
from AntShares.Fixed8 import Fixed8
from AntShares.Network.Inventory import Inventory
from AntShares.Network.InventoryType import InventoryType
from AntShares.Network.Mixins import InventoryMixin
from AntShares.Cryptography.Crypto import *
from AntShares.IO.MemoryStream import MemoryStream
import sys
import json


class Transaction(Inventory, InventoryMixin):


    Type = None

    Version = None

    Attributes = {}

    inputs = []

    outputs = []

    scripts = []

    systemFee = Fixed8(0)

    InventoryType = InventoryType.TX

    __network_fee = - Fixed8.Satoshi()

    __hash = None

    __references = {}


    """docstring for Transaction"""
    def __init__(self, inputs, outputs, attributes = {}, scripts=[] ):
        super(Transaction, self).__init__()
        self.inputs = inputs
        self.outputs = outputs
        self.Attributes= attributes
        self.scripts = []
        self.TransactionType = TransactionType.ContractTransaction
        self.InventoryType = 0x01  # InventoryType TX 0x01
        self.systemFee = self.SystemFee()


    def Hash(self):
        if not self.__hash:
            self.__hash = Crypto.Hash256( self.GetHashData())
        return self.__hash


    def NetworkFee(self):
        if self.__network_fee == -Fixed8.Satoshi():
#            Fixed8 input = References.Values.Where(p= > p.AssetId.Equals(Blockchain.SystemCoin.Hash)).Sum(p= > p.Value);
#            Fixed8 output = Outputs.Where(p= > p.AssetId.Equals(Blockchain.SystemCoin.Hash)).Sum(p= > p.Value);
#            _network_fee = input - output - SystemFee;
            pass

        return self.__network_fee


    def getAllInputs(self):
        return self.inputs


    def References(self):
        if self.__references is None:

            refs = set()


            for input in self.inputs:
                tx = Blockchain.Default().GetTransaction(input.PrevHash())

                if tx is not None:
                    #this aint right yet
                    refs.add({'input':input, 'output':tx.outputs[input.PrevIndex]})

            self.__references = refs
        return self.__references


    def Size(self):
        return sys.getsizeof(self.TransactionType) + sys.getsizeof(0) \
               + sys.getsizeof(self.Attributes) + sys.getsizeof(self.inputs) + \
                    sys.getsizeof(self.outputs) + sys.getsizeof(self.scripts)


    def SystemFee(self):

#        if (Settings.Default.SystemFee.ContainsKey(Type))
#            return Settings.Default.SystemFee[Type];
        return Fixed8(0)


    def Deserialize(self, reader):

        self.DeserializeUnsigned(reader)

        self.scripts = reader.readSerializableArray()
        self.OnDeserialized()


    def DeserializeExclusiveData(self, reader):
        pass

    @staticmethod
    def DeserializeFrom(reader):
        raise NotImplementedError()

    def DeserializeUnsigned(self, reader):
        if reader.readByte() != self.Type:
            raise Exception('incorrect type')
        self.DeserializeUnsignedWithoutType(reader)

    def DeserializeUnsignedWithoutType(self,reader):
        self.Version = reader.readByte()
        self.DeserializeExclusiveData(reader)
        self.Attributes = reader.readSerializableArray()
        self.inputs = [CoinReference(ref) for ref in reader.readSerializableArray()]
        self.outputs = [TransactionOutput(ref) for ref in reader.readSerializableArray()]


    def Equals(self, other):
        if other is None or other is not self:
            return False
        return self.Hash() == other.Hash()

    def getScriptHashesForVerifying(self):
        """Get ScriptHash From SignatureContract"""

        return []
#        if not self.__references:
#            raise Exception('No References to be verified')
#
#        hashes = [ref.ScriptHash() for ref in self.References()]

#        if (References == null) throw new InvalidOperationException();
#        HashSet < UInt160 > hashes = new HashSet < UInt160 > (Inputs.Select(p= > References[p].ScriptHash));
#        hashes.UnionWith(Attributes.Where(p= > p.Usage == TransactionAttributeUsage.Script).Select(p= > newUInt160(p.Data)));
#        foreach(var group in Outputs.GroupBy(p= > p.AssetId))
#        {
#            AssetState asset = Blockchain.Default.GetAssetState(group.Key);
#            if (asset == null) throw new InvalidOperationException();
#            if (asset.AssetType.HasFlag(AssetType.DutyFlag))
#            {
#                hashes.UnionWith(group.Select(p = > p.ScriptHash));
#            }
#        }
#        return hashes.OrderBy(p= > p).ToArray();
#
#        result = self.References()
#
#        if result == None:
#            raise Exception, 'getReference None.'
#
#        for _input in self.inputs:
#            _hash = result.get(_input.toString()).scriptHash
#            hashes.update({_hash.toString(), _hash})

        # TODO
        # Blockchain.getTransaction
#        txs = [Blockchain.getTransaction(output.AssetId) for output in self.outputs]
#        for output in self.outputs:
#            tx = txs[self.outputs.index(output)]
#            if tx == None:
#                raise Exception, "Tx == None"
#            else:
#                if tx.AssetType & AssetType.DutyFlag:
#                    hashes.update(output.ScriptHash.toString(), output.ScriptHash)
#
#                    array = sorted(hashes.keys())
#                    return array


    def GetTransactionResults(self):
        if self.References() is None: return None
        raise NotImplementedError()
#        return References.Values.Select(p= > new
#        {
#            AssetId = p.AssetId,
#                      Value = p.Value
#        }).Concat(Outputs.Select(p= > new
#        {
#            AssetId = p.AssetId,
#                      Value = -p.Value
#        })).GroupBy(p= > p.AssetId, (k, g) = > new
#        TransactionResult
#        {
#            AssetId = k,
#                      Amount = g.Sum(p= > p.Value)
#        }).Where(p= > p.Amount != Fixed8.Zero);


    def serialize(self, writer):
        self.serializeUnsigned(writer)
        writer.writeSerializableArray(self.scripts)

    def serializeUnsigned(self, writer):
        writer.writeByte(self.TransactionType)
        writer.writeByte(self.Version)
        self.serializeExclusiveData(writer)
        writer.writeSerializableArray(self.Attributes)
        writer.writeSerializableArray(self.inputs)
        writer.writeSerializableArray(self.outputs)

    def serializeExclusiveData(self, writer):
        # ReWrite in RegisterTransaction and IssueTransaction#
        pass


    def OnDeserialized(self):
        pass

    def ToJson(self):
        jsn = {}
        jsn["txid"] = self.Hash()
        jsn["size"] = self.Size()
        jsn["type"] = self.Type
        jsn["version"] = self.Version
        jsn["attributes"] = [attr.ToJson() for attr in self.Attributes]
        jsn["vout"] = [out.ToJson() for out in self.outputs]
        jsn["sys_fee"] = self.SystemFee()
        jsn["net_fee"] = self.NetworkFee()
        jsn["scripts"] = [script.ToJson() for script in self.scripts]

        return json.dumps(jsn)


    def Verify(self, mempool):
        for i in range(1, len(self.inputs)):
            j=0
            while j < i:
                j = j+1
                if self.inputs[i].PrevHash() == self.inputs[j].PrevHash() and self.inputs[i].PrevIndex() == self.inputs[j].PrevIndex():
                    return False

        for tx in mempool:
            if tx is not self:
                for ip in self.inputs:
                    if ip in tx.inputs:
                        return False

        if Blockchain.Default().IsDoubleSpend(self):
            return False


#            foreach (var group in Outputs.GroupBy(p => p.AssetId))
#            {
#                AssetState asset = Blockchain.Default.GetAssetState(group.Key)
#                if (asset == null) return false
#                foreach (TransactionOutput output in group)
#                    if (output.Value.GetData() % (long)Math.Pow(10, 8 - asset.Precision) != 0)
#                        return false
#            }
