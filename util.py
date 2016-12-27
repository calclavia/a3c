from keras import backend as K
from keras.layers import Dense, Input, Flatten, Dropout
from keras.layers.recurrent import LSTM
import numpy as np
from gym import spaces

def policy_loss(advantage):
    def categorical_crossentropy(y_true, y_pred):
        '''Expects a binary class matrix instead of a vector of scalar classes.
        '''
        return advantage * K.categorical_crossentropy(y_pred, y_true)
    return categorical_crossentropy

def discount_rewards(rewards, discount):
    """ Takes an array of rewards and compute array of discounted reward """
    discounted_r = np.zeros_like(rewards)
    current = 0

    for t in reversed(range(len(rewards))):
        current = current * discount + rewards[t]
        discounted_r[t] = current

    return discounted_r

def z_score(x):
    # z-score the rewards to be unit normal (variance control)
    std = np.std(x)

    if std != 0:
        return (x - np.mean(x)) / std
    return x - np.mean(x)

def space_to_shape(space):
    if isinstance(space, spaces.Discrete):
        # One hot vectors of states
        return (space.n,)
    return space.shape

def action_to_shape(space):
    return space.n if isinstance(space, spaces.Discrete) else space.shape

def one_hot(index, size):
    return [1 if index == i else 0 for i in range(size)]

def policy_loss(advantages):
    def loss(target, output):
        import tensorflow as tf
        # Target is a one-hot vector of actual action taken
        # Crossentropy weighted by advantage
        policy_loss = -K.sum(
            tf.diag(advantages) * target * K.log(output),
            len(output.get_shape()) - 1
        )

        return policy_loss
    return loss

def build_rnn(input_shape, num_outputs, time_steps, num_h):
    # Build Network
    inputs = Input(shape=(time_steps,) + input_shape, name='input')
    x = LSTM(num_h, activation='relu', name='hidden1')(inputs)
    x = Dropout(0.5)(x)
    outputs = Dense(num_outputs, activation='softmax', name='output')(x)
    return inputs, outputs
