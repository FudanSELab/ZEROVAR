import torch

class CodeT5Config:
    def __init__(
        self,
        name="codet5",
        mask_token="<extra_id_0>",
        max_len=20,
        train_batch_size=1,
        valid_batch_size=1,
        epochs=2,
        learning_rate=1e-5,
        adam_epsilon=1e-8,
        weight_decay=0,
        warmup_steps=0.1,
        max_grad_norm=1.0,
        train_sampling=None,
        valid_sampling=None,
        save_dir=None,
        log_step=500,
        cand_num=10,
        device="cuda"
    ):
        self.name = name
        self.mask_token = mask_token
        self.max_len = max_len
        self.train_batch_size=train_batch_size
        self.valid_batch_size=valid_batch_size
        self.epochs=epochs
        self.learning_rate=learning_rate
        self.adam_epsilon=adam_epsilon
        self.weight_decay=weight_decay
        self.warmup_steps=warmup_steps
        self.max_grad_norm=max_grad_norm
        self.train_sampling=train_sampling
        self.valid_sampling=valid_sampling
        self.save_dir=save_dir
        self.log_step=log_step
        self.cand_num=cand_num
        if not torch.cuda.is_available():
            self.device = "cpu"
        else:
            self.device = device

    def to_json(self):
        return {k:v for k, v in self.__dict__.items() if hasattr(self, k)}

    @classmethod
    def from_json(cls, json_data):
        config = CodeT5Config(json_data["name"])
        for k, v in json_data.items():
            if k == "name":
                continue
            setattr(config, k, v)
        return config	