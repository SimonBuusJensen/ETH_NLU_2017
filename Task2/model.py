import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np

class Model(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.tfconfig = tf.ConfigProto()
        self.model_dtype = tf.float32

        self.model_session = tf.Session(config=self.tfconfig)

    def build_forward_prop(self):

        print("building the forward model...")


        # initializer = tf.contrib.layers.xavier_initializer()

        # We suppose that all samples in one batch fall into the same bucket, i.e. have the same length with padding
        self.input_forward = tf.placeholder(dtype=self.model_dtype, shape=[None, None])
        decoder_inputs = tf.placeholder(dtype=self.model_dtype, shape=[None, None])
        # TODO: Maybe apply splitting word-wise

        # W_embeddings = tf.get_variable(name='W_emb', dtype=self.model_dtype, shape=[self.cfg["vocab_size"], self.cfg["embeddings_size"]],
                                    # initializer=initializer)
        # embeddings = tf.nn.embedding_lookup(params=W_embeddings, ids=self.input_forward)

        # state not used now
        self.outputs, state = tf.contrib.legacy_seq2seq.embedding_rnn_seq2seq(
            encoder_inputs = self.input_forward,
            decoder_inputs = decoder_inputs,
            cell = tf.contrib.rnn.BasicLSTMCell(self.config["lstm_size"]),
            num_encoder_symbols = self.cfg["vocab_size"],
            num_decoder_symbols = self.cfg["vocab_size"],
            embedding_size = self.cfg["embeddings_size"],
            # output_projection=None,
            feed_previous=False,
            dtype=self.model_dtype
            # scope=None
        )

    def build_backprop(self):
        print("building the backprop model...")

        # TODO: Exclude first token of each sentence (<bos> tag)
        labs = tf.slice(self.input_forward, [0, 1], [-1, -1])

        # TODO: how is unrolling done here?
        logs = self.outputs

        self.total_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                            labels=labs, logits=logs)
        optimizer = tf.train.AdamOptimizer()

        # Clipped gradients
        gvs = optimizer.compute_gradients(self.total_loss)
        grads = [x[0] for x in gvs]
        vars = [x[1] for x in gvs]

        clipped_grads, _ = tf.clip_by_global_norm(t_list=grads, clip_norm=10)  # second output not used
        self.train_op = optimizer.apply_gradients(list(zip(clipped_grads, vars)))

    def validation_loss(self, data):
        return ""

    def train(self, train_data, test_data):
        # Initialize variables
        if "load_model_path" in self.cfg:
            self.load_model(self.model_session, self.cfg["load_model_path"])
        else:
            tf.global_variables_initializer().run(session=self.model_session)

        for e in range(self.cfg["max_iterations"]):
            print("Starting epoch %d..." % e)
            start_epoch = start_batches = time.time()

            batch_indices = self.define_minibatches(train_data.shape[0])

            #TODO adapt this
            for i, batch_idx in enumerate(batch_indices):
                batch = train_data[batch_idx]

                food = {
                    self.input_forward: batch,
                    # self.initial_hidden: np.zeros((len(batch_idx), self.cfg["lstm_size"])),
                    # self.initial_cell: np.zeros((len(batch_idx), self.cfg["lstm_size"]))
                }

                self.model_session.run(fetches=self.train_op, feed_dict=food)

                # Log test loss every so often
                if self.cfg["out_batch"] > 0 and i > 0 and (i % (self.cfg["out_batch"]) == 0) :
                    print("\tBatch chunk %d - %d finished in %d seconds" % (i-self.cfg["out_batch"], i, time.time() - start_batches))
                    print("\tTest loss (mean per sentence) at batch %d: %f" % (i, float(self.validation_loss(test_data))))
                    start_batches = time.time()

            print("Epoch completed in %d seconds." % (time.time() - start_epoch))

        if "save_model_path" in self.cfg:
            self.save_model(path=self.cfg["save_model_path"])

    def test(self, data):
        pass

    def save_model(self, path):
        saver = tf.train.Saver()
        save_path = saver.save(self.model_session, path)
        print("Model saved in file: %s" % save_path)
        config.save_cfg(path)


    def load_model(self, path):
        saver = tf.train.Saver()
        saver.restore(self.model_session, path)
        print("Model from %s restored" % path)

    
    # TODO adapt this to task 2 and buckets
    def define_minibatches(self, length, permute=True):
        if permute:
            # create a random permutation (for training over multiple epochs)
            indices = np.random.permutation(length)
        else:
            # use the indices in a sequential manner (for testing)
            indices = np.arange(length)

        # Hold out the last sentences in case data set is not divisible by the batch size
        rest = length % self.cfg["batch_size"]
        if rest is not 0:
            indices_even = indices[:-rest]
            indices_rest = indices[len(indices_even):]
            batches = np.split(indices_even, indices_or_sections=len(indices_even) / self.cfg["batch_size"])
            batches.append(np.array(indices_rest))
        else:
            batches = np.split(indices, indices_or_sections=len(indices) / self.cfg["batch_size"])



        return batches