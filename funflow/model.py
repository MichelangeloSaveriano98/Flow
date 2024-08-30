from typing import Any, Self
from .layer import Layer
from .template_engine import create_graph


class Model(Layer):
    def __init__(self,
                 layers: Layer | list[Layer] = None,
                 inputs: list[str] = None,
                 outputs: list[str] = None,
                 **kwargs
                 ):
        super().__init__(
            inputs=inputs,
            outputs=outputs,
            input_type="kwargs",
            output_type="dict",
            **kwargs
        )

        if isinstance(layers, Layer):
            layers = [layers]

        self._layers = layers if layers is not None else []
        # self._state = dict()

    def add_layer(self, layer: Layer) -> Self:
        self._layers.append(layer)
        return self

    def call(self, **kwargs: Any) -> Any:
        state = dict()
        state.update(kwargs)

        topological_order, state_producer = create_graph(self._layers, state)

        for layers in topological_order:

            # INFO: this could be parallelized
            for layer in layers:
                actual_input_names = layer.actual_inputs

                layer_inputs = {name: state[name] for name in actual_input_names}
                layer_outputs = layer(**layer_inputs)
                state.update(layer_outputs)

        return state